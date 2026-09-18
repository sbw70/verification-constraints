#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdio.h>
#include <errno.h>
#include <unistd.h>

#include "esp_err.h"
#include "esp_event.h"
#include "esp_log.h"
#include "esp_netif.h"
#include "esp_wifi.h"

#include "freertos/FreeRTOS.h"
#include "freertos/event_groups.h"
#include "freertos/task.h"

#include "driver/ledc.h"

#include "lwip/inet.h"
#include "lwip/sockets.h"

#include "nvs.h"
#include "nvs_flash.h"

#include "psa/crypto.h"

#include "monocypher-ed25519.h"

#include "local_wifi_config.h"

static const char *TAG = "ESP_LOCAL_006";

/* --------------------------------------------------------------------------
 * ESP-LOCAL-006
 *
 * Hostile-relay endpoint runtime.
 *
 * Transport is not authority.
 *
 * Evaluation order:
 *
 *   receive relay envelope
 *       ->
 *   decode authority + signature
 *       ->
 *   provider Ed25519 signature
 *       ->
 *   semantic admissibility
 *       ->
 *   SHA-256 authority binding
 *       ->
 *   persistent-state validity
 *       ->
 *   exact authority-id match
 *       ->
 *   spent check
 *       ->
 *   durable consume
 *       ->
 *   durable read-back verification
 *       ->
 *   physical PWM command
 *
 * Missing, malformed, corrupt, unreadable, wrong-version, wrong-authority,
 * spent, unsigned, incorrectly signed, semantically enlarged, or otherwise
 * ambiguous input never becomes executable authority.
 *
 * No NVS auto-erase/recovery path exists.
 * -------------------------------------------------------------------------- */


/* --------------------------------------------------------------------------
 * Network
 * -------------------------------------------------------------------------- */

#define RELAY_LISTEN_PORT       19061
#define LISTEN_BACKLOG          4

#define MAX_REQUEST_LINE        2048
#define MAX_AUTHORITY_B64       1024
#define MAX_SIGNATURE_B64       128
#define MAX_AUTHORITY_BYTES     768

#define WIFI_CONNECTED_BIT      BIT0
#define WIFI_FAIL_BIT           BIT1
#define WIFI_MAX_RETRIES        10

static EventGroupHandle_t s_wifi_event_group = NULL;
static int s_wifi_retry_count = 0;


/* --------------------------------------------------------------------------
 * Hardware
 * -------------------------------------------------------------------------- */

#define SERVO_GPIO              5

#define SERVO_PWM_HZ            50
#define SERVO_HOLD_MS           1000

#define SERVO_LEDC_MODE         LEDC_LOW_SPEED_MODE
#define SERVO_LEDC_TIMER        LEDC_TIMER_0
#define SERVO_LEDC_CHANNEL      LEDC_CHANNEL_0
#define SERVO_LEDC_RESOLUTION   LEDC_TIMER_14_BIT

#define SERVO_DUTY_2MS          1638U


/* --------------------------------------------------------------------------
 * Persistent authority state
 * -------------------------------------------------------------------------- */

#define NUVL_STATE_MAGIC        0x4E55564CUL
#define NUVL_STATE_VERSION      1U

#define NUVL_PARTITION          "nuvl_state"
#define NUVL_NVS_NAMESPACE      "nuvl_auth"
#define NUVL_NVS_STATE_KEY      "state"

#define NUVL_AUTHORITY_ID_LEN   32U

typedef enum {
    NUVL_AUTH_STATE_UNSPENT = 1,
    NUVL_AUTH_STATE_SPENT   = 2
} nuvl_auth_state_t;

typedef struct {
    uint32_t magic;
    uint16_t version;
    uint8_t  state;
    uint8_t  reserved;
    uint8_t  authority_id[NUVL_AUTHORITY_ID_LEN];
    uint32_t crc32;
} nuvl_state_record_t;

_Static_assert(
    sizeof(nuvl_state_record_t) == 44,
    "Unexpected persistent authority record size"
);


/* --------------------------------------------------------------------------
 * Provider trust anchor
 * -------------------------------------------------------------------------- */

static const uint8_t PROVIDER_PUBLIC_KEY[32] = {
    0x48, 0x85, 0x22, 0x70, 0xce, 0x16, 0x65, 0x4e,
    0xde, 0xef, 0x2a, 0x1c, 0x3d, 0x09, 0x30, 0xaf,
    0x4b, 0x99, 0x0e, 0x1b, 0xf5, 0x06, 0x0f, 0xb3,
    0x22, 0x19, 0x96, 0x43, 0x4f, 0x63, 0xe5, 0xb1
};


/* --------------------------------------------------------------------------
 * Canonical semantic bounds
 *
 * Fresh nonces are allowed. All authority-bearing fields are otherwise fixed.
 *
 * Exact signed form:
 *
 * {"action":"move_servo","context":"esp_local_006",
 *  "device_id":"esp32-xiao-servo-02","max_uses":1,
 *  "nonce":"<32 lowercase hex chars>"}
 * -------------------------------------------------------------------------- */

static const char AUTHORITY_PREFIX[] =
    "{\"action\":\"move_servo\","
    "\"context\":\"esp_local_006\","
    "\"device_id\":\"esp32-xiao-servo-02\","
    "\"max_uses\":1,"
    "\"nonce\":\"";


/* --------------------------------------------------------------------------
 * CRC32
 * -------------------------------------------------------------------------- */

static uint32_t nuvl_crc32(const uint8_t *data, size_t length)
{
    uint32_t crc = 0xFFFFFFFFU;

    for (size_t i = 0; i < length; ++i) {
        crc ^= data[i];

        for (unsigned bit = 0; bit < 8; ++bit) {
            if (crc & 1U) {
                crc = (crc >> 1U) ^ 0xEDB88320U;
            } else {
                crc >>= 1U;
            }
        }
    }

    return crc ^ 0xFFFFFFFFU;
}


/* --------------------------------------------------------------------------
 * Lowercase hex helper
 * -------------------------------------------------------------------------- */

static bool is_lower_hex_char(uint8_t c)
{
    return ((c >= (uint8_t)'0') && (c <= (uint8_t)'9')) ||
           ((c >= (uint8_t)'a') && (c <= (uint8_t)'f'));
}


/* --------------------------------------------------------------------------
 * Strict standard-base64 decoder
 * -------------------------------------------------------------------------- */

static int base64_value(char c)
{
    if ((c >= 'A') && (c <= 'Z')) {
        return c - 'A';
    }

    if ((c >= 'a') && (c <= 'z')) {
        return 26 + (c - 'a');
    }

    if ((c >= '0') && (c <= '9')) {
        return 52 + (c - '0');
    }

    if (c == '+') {
        return 62;
    }

    if (c == '/') {
        return 63;
    }

    return -1;
}


static bool strict_base64_decode(
    const char *input,
    uint8_t *output,
    size_t output_capacity,
    size_t *output_length
)
{
    if ((input == NULL) ||
        (output == NULL) ||
        (output_length == NULL)) {
        return false;
    }

    size_t length = strlen(input);

    if ((length == 0U) || ((length % 4U) != 0U)) {
        return false;
    }

    size_t out = 0U;

    for (size_t i = 0U; i < length; i += 4U) {
        bool last = (i + 4U == length);

        int v0 = base64_value(input[i + 0U]);
        int v1 = base64_value(input[i + 1U]);

        if ((v0 < 0) || (v1 < 0)) {
            return false;
        }

        char c2 = input[i + 2U];
        char c3 = input[i + 3U];

        bool pad2 = (c2 == '=');
        bool pad3 = (c3 == '=');

        if ((pad2 || pad3) && !last) {
            return false;
        }

        if (pad2 && !pad3) {
            return false;
        }

        int v2 = pad2 ? 0 : base64_value(c2);
        int v3 = pad3 ? 0 : base64_value(c3);

        if ((v2 < 0) || (v3 < 0)) {
            return false;
        }

        size_t bytes_this_block = pad2 ? 1U : (pad3 ? 2U : 3U);

        if ((out + bytes_this_block) > output_capacity) {
            return false;
        }

        uint32_t group =
            ((uint32_t)v0 << 18U) |
            ((uint32_t)v1 << 12U) |
            ((uint32_t)v2 << 6U) |
            (uint32_t)v3;

        output[out++] = (uint8_t)((group >> 16U) & 0xFFU);

        if (!pad2) {
            output[out++] = (uint8_t)((group >> 8U) & 0xFFU);
        }

        if (!pad3) {
            output[out++] = (uint8_t)(group & 0xFFU);
        }

        if (pad2) {
            if ((v1 & 0x0FU) != 0) {
                return false;
            }
        } else if (pad3) {
            if ((v2 & 0x03U) != 0) {
                return false;
            }
        }
    }

    *output_length = out;
    return true;
}


/* --------------------------------------------------------------------------
 * Strict relay-envelope parser
 *
 * Accepted wire shape:
 * {"authority_b64":"...","signature_b64":"..."}
 * -------------------------------------------------------------------------- */

static bool parse_relay_envelope(
    const char *line,
    char *authority_b64,
    size_t authority_b64_capacity,
    char *signature_b64,
    size_t signature_b64_capacity
)
{
    static const char prefix[] = "{\"authority_b64\":\"";
    static const char middle[] = "\",\"signature_b64\":\"";
    static const char suffix[] = "\"}";

    if ((line == NULL) ||
        (authority_b64 == NULL) ||
        (signature_b64 == NULL)) {
        return false;
    }

    size_t line_length = strlen(line);
    size_t prefix_length = strlen(prefix);
    size_t middle_length = strlen(middle);
    size_t suffix_length = strlen(suffix);

    if (line_length <= (prefix_length + middle_length + suffix_length)) {
        return false;
    }

    if (memcmp(line, prefix, prefix_length) != 0) {
        return false;
    }

    const char *authority_start = line + prefix_length;
    const char *middle_at = strstr(authority_start, middle);

    if (middle_at == NULL) {
        return false;
    }

    const char *signature_start = middle_at + middle_length;
    const char *suffix_at = strstr(signature_start, suffix);

    if (suffix_at == NULL) {
        return false;
    }

    if ((suffix_at + suffix_length) != (line + line_length)) {
        return false;
    }

    size_t authority_length = (size_t)(middle_at - authority_start);
    size_t signature_length = (size_t)(suffix_at - signature_start);

    if ((authority_length == 0U) ||
        (signature_length == 0U) ||
        (authority_length >= authority_b64_capacity) ||
        (signature_length >= signature_b64_capacity)) {
        return false;
    }

    memcpy(authority_b64, authority_start, authority_length);
    authority_b64[authority_length] = '\0';

    memcpy(signature_b64, signature_start, signature_length);
    signature_b64[signature_length] = '\0';

    return true;
}


/* --------------------------------------------------------------------------
 * Semantic admissibility
 * -------------------------------------------------------------------------- */

static bool authority_is_admissible(
    const uint8_t *authority,
    size_t authority_length
)
{
    if (authority == NULL) {
        return false;
    }

    size_t prefix_length = strlen(AUTHORITY_PREFIX);
    size_t expected_length = prefix_length + 32U + 2U;

    if (authority_length != expected_length) {
        ESP_LOGE(TAG, "Authority semantic length mismatch");
        return false;
    }

    if (memcmp(
            authority,
            AUTHORITY_PREFIX,
            prefix_length
        ) != 0) {
        ESP_LOGE(TAG, "Authority outside configured admissibility");
        return false;
    }

    const uint8_t *nonce = authority + prefix_length;

    for (size_t i = 0U; i < 32U; ++i) {
        if (!is_lower_hex_char(nonce[i])) {
            ESP_LOGE(TAG, "Authority nonce encoding invalid");
            return false;
        }
    }

    if ((authority[prefix_length + 32U] != (uint8_t)'"') ||
        (authority[prefix_length + 33U] != (uint8_t)'}')) {
        ESP_LOGE(TAG, "Authority canonical termination invalid");
        return false;
    }

    ESP_LOGI(TAG, "006_SEMANTIC_ADMISSIBILITY_PASS");
    return true;
}


/* --------------------------------------------------------------------------
 * SHA-256 authority identifier
 * -------------------------------------------------------------------------- */

static bool authority_sha256(
    const uint8_t *authority,
    size_t authority_length,
    uint8_t output[32]
)
{
    size_t output_length = 0U;

    psa_status_t status = psa_hash_compute(
        PSA_ALG_SHA_256,
        authority,
        authority_length,
        output,
        32U,
        &output_length
    );

    if ((status != PSA_SUCCESS) || (output_length != 32U)) {
        ESP_LOGE(
            TAG,
            "SHA-256 authority binding failed: status=%ld len=%u",
            (long)status,
            (unsigned)output_length
        );
        return false;
    }

    return true;
}


/* --------------------------------------------------------------------------
 * Persistent-record validation
 * -------------------------------------------------------------------------- */

static bool validate_state_record(const nuvl_state_record_t *record)
{
    if (record == NULL) {
        ESP_LOGE(TAG, "Persistent record pointer is null");
        return false;
    }

    if (record->magic != NUVL_STATE_MAGIC) {
        ESP_LOGE(TAG, "Persistent record magic mismatch");
        return false;
    }

    if (record->version != NUVL_STATE_VERSION) {
        ESP_LOGE(
            TAG,
            "Persistent record version mismatch: %u",
            (unsigned)record->version
        );
        return false;
    }

    if (record->reserved != 0U) {
        ESP_LOGE(TAG, "Persistent record reserved field invalid");
        return false;
    }

    if ((record->state != NUVL_AUTH_STATE_UNSPENT) &&
        (record->state != NUVL_AUTH_STATE_SPENT)) {
        ESP_LOGE(
            TAG,
            "Persistent record state invalid: %u",
            (unsigned)record->state
        );
        return false;
    }

    uint32_t expected_crc = nuvl_crc32(
        (const uint8_t *)record,
        offsetof(nuvl_state_record_t, crc32)
    );

    if (record->crc32 != expected_crc) {
        ESP_LOGE(
            TAG,
            "Persistent record CRC mismatch: stored=%08lx expected=%08lx",
            (unsigned long)record->crc32,
            (unsigned long)expected_crc
        );
        return false;
    }

    return true;
}


/* --------------------------------------------------------------------------
 * Persistent-state read
 * -------------------------------------------------------------------------- */

static bool load_state_record(nuvl_state_record_t *record)
{
    nvs_handle_t handle;
    esp_err_t err;
    size_t required_size = 0U;

    if (record == NULL) {
        return false;
    }

    err = nvs_open_from_partition(
        NUVL_PARTITION,
        NUVL_NVS_NAMESPACE,
        NVS_READONLY,
        &handle
    );

    if (err != ESP_OK) {
        ESP_LOGE(
            TAG,
            "Unable to open authority state: %s",
            esp_err_to_name(err)
        );
        return false;
    }

    err = nvs_get_blob(
        handle,
        NUVL_NVS_STATE_KEY,
        NULL,
        &required_size
    );

    if (err == ESP_ERR_NVS_NOT_FOUND) {
        ESP_LOGE(TAG, "Persistent authority state is missing");
        nvs_close(handle);
        return false;
    }

    if (err != ESP_OK) {
        ESP_LOGE(
            TAG,
            "Unable to determine authority-state size: %s",
            esp_err_to_name(err)
        );
        nvs_close(handle);
        return false;
    }

    if (required_size != sizeof(*record)) {
        ESP_LOGE(
            TAG,
            "Persistent authority-state size invalid: %u",
            (unsigned)required_size
        );
        nvs_close(handle);
        return false;
    }

    size_t read_size = sizeof(*record);

    err = nvs_get_blob(
        handle,
        NUVL_NVS_STATE_KEY,
        record,
        &read_size
    );

    nvs_close(handle);

    if (err != ESP_OK) {
        ESP_LOGE(
            TAG,
            "Unable to read authority state: %s",
            esp_err_to_name(err)
        );
        return false;
    }

    if (read_size != sizeof(*record)) {
        ESP_LOGE(TAG, "Persistent authority read length changed");
        return false;
    }

    if (!validate_state_record(record)) {
        ESP_LOGE(TAG, "Persistent authority state failed validation");
        return false;
    }

    return true;
}


/* --------------------------------------------------------------------------
 * Durable consumption
 * -------------------------------------------------------------------------- */

static bool durable_consume(const uint8_t expected_authority_id[32])
{
    nvs_handle_t handle;
    esp_err_t err;
    nuvl_state_record_t record;
    size_t size = sizeof(record);

    err = nvs_open_from_partition(
        NUVL_PARTITION,
        NUVL_NVS_NAMESPACE,
        NVS_READWRITE,
        &handle
    );

    if (err != ESP_OK) {
        ESP_LOGE(
            TAG,
            "Unable to open authority state for consumption: %s",
            esp_err_to_name(err)
        );
        return false;
    }

    err = nvs_get_blob(
        handle,
        NUVL_NVS_STATE_KEY,
        &record,
        &size
    );

    if (err != ESP_OK) {
        ESP_LOGE(
            TAG,
            "Unable to reread authority before consumption: %s",
            esp_err_to_name(err)
        );
        nvs_close(handle);
        return false;
    }

    if (size != sizeof(record)) {
        ESP_LOGE(TAG, "Authority size invalid immediately before consumption");
        nvs_close(handle);
        return false;
    }

    if (!validate_state_record(&record)) {
        ESP_LOGE(TAG, "Authority invalid immediately before consumption");
        nvs_close(handle);
        return false;
    }

    if (memcmp(
            record.authority_id,
            expected_authority_id,
            32U
        ) != 0) {
        ESP_LOGE(TAG, "Authority ID mismatch immediately before consumption");
        nvs_close(handle);
        return false;
    }

    if (record.state != NUVL_AUTH_STATE_UNSPENT) {
        ESP_LOGW(TAG, "Authority already spent");
        nvs_close(handle);
        return false;
    }

    record.state = NUVL_AUTH_STATE_SPENT;
    record.crc32 = nuvl_crc32(
        (const uint8_t *)&record,
        offsetof(nuvl_state_record_t, crc32)
    );

    err = nvs_set_blob(
        handle,
        NUVL_NVS_STATE_KEY,
        &record,
        sizeof(record)
    );

    if (err != ESP_OK) {
        ESP_LOGE(
            TAG,
            "Unable to write SPENT state: %s",
            esp_err_to_name(err)
        );
        nvs_close(handle);
        return false;
    }

    err = nvs_commit(handle);

    if (err != ESP_OK) {
        ESP_LOGE(
            TAG,
            "Unable to commit SPENT state: %s",
            esp_err_to_name(err)
        );
        nvs_close(handle);
        return false;
    }

    nvs_close(handle);

    err = nvs_flash_deinit_partition(NUVL_PARTITION);

    if (err != ESP_OK) {
        ESP_LOGE(
            TAG,
            "Unable to deinitialize state partition after commit: %s",
            esp_err_to_name(err)
        );
        return false;
    }

    err = nvs_flash_init_partition(NUVL_PARTITION);

    if (err != ESP_OK) {
        ESP_LOGE(
            TAG,
            "Unable to reinitialize state partition after commit: %s",
            esp_err_to_name(err)
        );
        return false;
    }

    nuvl_state_record_t verify_record;

    if (!load_state_record(&verify_record)) {
        ESP_LOGE(TAG, "Fresh persistent reread failed");
        return false;
    }

    if (memcmp(
            verify_record.authority_id,
            expected_authority_id,
            32U
        ) != 0) {
        ESP_LOGE(TAG, "Fresh persistent reread authority ID mismatch");
        return false;
    }

    if (verify_record.state != NUVL_AUTH_STATE_SPENT) {
        ESP_LOGE(TAG, "Fresh persistent reread did not confirm SPENT");
        return false;
    }

    ESP_LOGI(TAG, "006_DURABLE_SPENT_REREAD_PASS");
    return true;
}


/* --------------------------------------------------------------------------
 * PWM command
 * -------------------------------------------------------------------------- */

static bool issue_servo_pwm(void)
{
    ledc_timer_config_t timer_config = {
        .speed_mode       = SERVO_LEDC_MODE,
        .duty_resolution  = SERVO_LEDC_RESOLUTION,
        .timer_num        = SERVO_LEDC_TIMER,
        .freq_hz          = SERVO_PWM_HZ,
        .clk_cfg          = LEDC_AUTO_CLK
    };

    esp_err_t err = ledc_timer_config(&timer_config);

    if (err != ESP_OK) {
        ESP_LOGE(
            TAG,
            "LEDC timer configuration failed: %s",
            esp_err_to_name(err)
        );
        return false;
    }

    ledc_channel_config_t channel_config = {
        .gpio_num   = SERVO_GPIO,
        .speed_mode = SERVO_LEDC_MODE,
        .channel    = SERVO_LEDC_CHANNEL,
        .intr_type  = LEDC_INTR_DISABLE,
        .timer_sel  = SERVO_LEDC_TIMER,
        .duty       = 0,
        .hpoint     = 0,
        .flags.output_invert = 0
    };

    err = ledc_channel_config(&channel_config);

    if (err != ESP_OK) {
        ESP_LOGE(
            TAG,
            "LEDC channel configuration failed: %s",
            esp_err_to_name(err)
        );
        return false;
    }

    err = ledc_set_duty(
        SERVO_LEDC_MODE,
        SERVO_LEDC_CHANNEL,
        SERVO_DUTY_2MS
    );

    if (err != ESP_OK) {
        ESP_LOGE(
            TAG,
            "Unable to set servo duty: %s",
            esp_err_to_name(err)
        );
        return false;
    }

    err = ledc_update_duty(
        SERVO_LEDC_MODE,
        SERVO_LEDC_CHANNEL
    );

    if (err != ESP_OK) {
        ESP_LOGE(
            TAG,
            "Unable to update servo duty: %s",
            esp_err_to_name(err)
        );
        return false;
    }

    ESP_LOGI(TAG, "006_PWM_COMMAND_BEGIN");

    vTaskDelay(pdMS_TO_TICKS(SERVO_HOLD_MS));

    err = ledc_set_duty(
        SERVO_LEDC_MODE,
        SERVO_LEDC_CHANNEL,
        0
    );

    if (err != ESP_OK) {
        ESP_LOGE(
            TAG,
            "Unable to clear servo duty: %s",
            esp_err_to_name(err)
        );
        return false;
    }

    err = ledc_update_duty(
        SERVO_LEDC_MODE,
        SERVO_LEDC_CHANNEL
    );

    if (err != ESP_OK) {
        ESP_LOGE(
            TAG,
            "Unable to apply zero servo duty: %s",
            esp_err_to_name(err)
        );
        return false;
    }

    ESP_LOGI(TAG, "006_PWM_COMMAND_END");
    return true;
}


/* --------------------------------------------------------------------------
 * Request processing
 * -------------------------------------------------------------------------- */

static const char *process_request(const char *line)
{
    char authority_b64[MAX_AUTHORITY_B64];
    char signature_b64[MAX_SIGNATURE_B64];

    uint8_t authority[MAX_AUTHORITY_BYTES];
    uint8_t signature[64];

    size_t authority_length = 0U;
    size_t signature_length = 0U;

    if (!parse_relay_envelope(
            line,
            authority_b64,
            sizeof(authority_b64),
            signature_b64,
            sizeof(signature_b64)
        )) {
        ESP_LOGW(TAG, "006_DENY_MALFORMED_ENVELOPE");
        return "malformed_envelope";
    }

    if (!strict_base64_decode(
            authority_b64,
            authority,
            sizeof(authority),
            &authority_length
        )) {
        ESP_LOGW(TAG, "006_DENY_AUTHORITY_BASE64");
        return "authority_base64_invalid";
    }

    if (!strict_base64_decode(
            signature_b64,
            signature,
            sizeof(signature),
            &signature_length
        )) {
        ESP_LOGW(TAG, "006_DENY_SIGNATURE_BASE64");
        return "signature_base64_invalid";
    }

    if (signature_length != sizeof(signature)) {
        ESP_LOGW(TAG, "006_DENY_SIGNATURE_LENGTH");
        return "signature_length_invalid";
    }

    int signature_result = crypto_ed25519_check(
        signature,
        PROVIDER_PUBLIC_KEY,
        authority,
        authority_length
    );

    if (signature_result != 0) {
        ESP_LOGW(TAG, "006_DENY_SIGNATURE_INVALID");
        return "signature_invalid";
    }

    ESP_LOGI(TAG, "006_SIGNATURE_VALID");

    if (!authority_is_admissible(
            authority,
            authority_length
        )) {
        ESP_LOGW(TAG, "006_DENY_SEMANTIC");
        return "semantic_denied";
    }

    uint8_t authority_id[32];

    if (!authority_sha256(
            authority,
            authority_length,
            authority_id
        )) {
        ESP_LOGE(TAG, "006_DENY_AUTHORITY_HASH_FAILURE");
        return "authority_hash_failure";
    }

    nuvl_state_record_t state;

    if (!load_state_record(&state)) {
        ESP_LOGW(TAG, "006_DENY_STATE_INVALID");
        return "state_invalid";
    }

    if (memcmp(
            state.authority_id,
            authority_id,
            sizeof(authority_id)
        ) != 0) {
        ESP_LOGW(TAG, "006_DENY_AUTHORITY_STATE_MISMATCH");
        return "authority_state_mismatch";
    }

    if (state.state == NUVL_AUTH_STATE_SPENT) {
        ESP_LOGW(TAG, "006_DENY_REPLAY_SPENT");
        return "replay_spent";
    }

    if (state.state != NUVL_AUTH_STATE_UNSPENT) {
        ESP_LOGW(TAG, "006_DENY_STATE_NOT_UNSPENT");
        return "state_not_unspent";
    }

    ESP_LOGI(TAG, "006_AUTHORITY_UNSPENT_PASS");

    if (!durable_consume(authority_id)) {
        ESP_LOGE(TAG, "006_DENY_DURABLE_CONSUME_FAILURE");
        return "durable_consume_failure";
    }

    /*
     * After durable consumption, no later failure may restore authority.
     * Availability may be lost; authority may not be regenerated.
     */
    if (!issue_servo_pwm()) {
        ESP_LOGE(TAG, "006_PWM_FAILED_AFTER_DURABLE_SPEND");
        return "pwm_failed_after_spend";
    }

    ESP_LOGI(TAG, "006_ACCEPT_EXECUTED");
    return NULL;
}


/* --------------------------------------------------------------------------
 * Socket helpers
 * -------------------------------------------------------------------------- */

static bool recv_request_line(
    int sock,
    char *buffer,
    size_t capacity
)
{
    if ((buffer == NULL) || (capacity < 2U)) {
        return false;
    }

    size_t used = 0U;
    bool saw_newline = false;

    while (used < (capacity - 1U)) {
        ssize_t received = recv(
            sock,
            buffer + used,
            capacity - 1U - used,
            0
        );

        if (received < 0) {
            ESP_LOGE(TAG, "Socket recv failed: errno=%d", errno);
            return false;
        }

        if (received == 0) {
            break;
        }

        size_t old_used = used;
        used += (size_t)received;

        char *newline = memchr(
            buffer + old_used,
            '\n',
            (size_t)received
        );

        if (newline != NULL) {
            used = (size_t)(newline - buffer);
            saw_newline = true;
            break;
        }
    }

    if (used == 0U) {
        return false;
    }

    if (!saw_newline && (used == (capacity - 1U))) {
        ESP_LOGW(TAG, "Request line exceeds maximum length");
        return false;
    }

    if ((used > 0U) && (buffer[used - 1U] == '\r')) {
        --used;
    }

    buffer[used] = '\0';
    return true;
}


static void send_response(
    int sock,
    bool accepted,
    const char *reason
)
{
    char response[192];

    if (accepted) {
        snprintf(
            response,
            sizeof(response),
            "{\"status\":\"accepted\",\"reason\":\"executed\"}\n"
        );
    } else {
        snprintf(
            response,
            sizeof(response),
            "{\"status\":\"denied\",\"reason\":\"%s\"}\n",
            (reason != NULL) ? reason : "unspecified"
        );
    }

    size_t length = strlen(response);
    size_t sent_total = 0U;

    while (sent_total < length) {
        ssize_t sent = send(
            sock,
            response + sent_total,
            length - sent_total,
            0
        );

        if (sent <= 0) {
            break;
        }

        sent_total += (size_t)sent;
    }
}


/* --------------------------------------------------------------------------
 * Wi-Fi
 * -------------------------------------------------------------------------- */

static void wifi_event_handler(
    void *arg,
    esp_event_base_t event_base,
    int32_t event_id,
    void *event_data
)
{
    (void)arg;

    if ((event_base == WIFI_EVENT) &&
        (event_id == WIFI_EVENT_STA_START)) {
        esp_wifi_connect();
        return;
    }

    if ((event_base == WIFI_EVENT) &&
        (event_id == WIFI_EVENT_STA_DISCONNECTED)) {

        if (s_wifi_retry_count < WIFI_MAX_RETRIES) {
            ++s_wifi_retry_count;

            ESP_LOGW(
                TAG,
                "Wi-Fi disconnected; reconnect attempt %d/%d",
                s_wifi_retry_count,
                WIFI_MAX_RETRIES
            );

            esp_wifi_connect();
        } else if (s_wifi_event_group != NULL) {
            xEventGroupSetBits(
                s_wifi_event_group,
                WIFI_FAIL_BIT
            );
        }

        return;
    }

    if ((event_base == IP_EVENT) &&
        (event_id == IP_EVENT_STA_GOT_IP)) {

        ip_event_got_ip_t *event =
            (ip_event_got_ip_t *)event_data;

        ESP_LOGI(
            TAG,
            "006_WIFI_GOT_IP " IPSTR,
            IP2STR(&event->ip_info.ip)
        );

        s_wifi_retry_count = 0;

        if (s_wifi_event_group != NULL) {
            xEventGroupSetBits(
                s_wifi_event_group,
                WIFI_CONNECTED_BIT
            );
        }
    }
}


static bool wifi_connect(void)
{
    s_wifi_event_group = xEventGroupCreate();

    if (s_wifi_event_group == NULL) {
        ESP_LOGE(TAG, "Unable to allocate Wi-Fi event group");
        return false;
    }

    esp_err_t err = esp_netif_init();

    if (err != ESP_OK) {
        ESP_LOGE(
            TAG,
            "esp_netif_init failed: %s",
            esp_err_to_name(err)
        );
        return false;
    }

    err = esp_event_loop_create_default();

    if (err != ESP_OK) {
        ESP_LOGE(
            TAG,
            "esp_event_loop_create_default failed: %s",
            esp_err_to_name(err)
        );
        return false;
    }

    esp_netif_t *station = esp_netif_create_default_wifi_sta();

    if (station == NULL) {
        ESP_LOGE(TAG, "Unable to create default Wi-Fi station");
        return false;
    }

    wifi_init_config_t init_config = WIFI_INIT_CONFIG_DEFAULT();

    err = esp_wifi_init(&init_config);

    if (err != ESP_OK) {
        ESP_LOGE(
            TAG,
            "esp_wifi_init failed: %s",
            esp_err_to_name(err)
        );
        return false;
    }

    err = esp_event_handler_instance_register(
        WIFI_EVENT,
        ESP_EVENT_ANY_ID,
        &wifi_event_handler,
        NULL,
        NULL
    );

    if (err != ESP_OK) {
        ESP_LOGE(
            TAG,
            "Wi-Fi event registration failed: %s",
            esp_err_to_name(err)
        );
        return false;
    }

    err = esp_event_handler_instance_register(
        IP_EVENT,
        IP_EVENT_STA_GOT_IP,
        &wifi_event_handler,
        NULL,
        NULL
    );

    if (err != ESP_OK) {
        ESP_LOGE(
            TAG,
            "IP event registration failed: %s",
            esp_err_to_name(err)
        );
        return false;
    }

    wifi_config_t wifi_config = {0};

    size_t ssid_length = strlen(ESP_LOCAL_006_WIFI_SSID);
    size_t password_length = strlen(ESP_LOCAL_006_WIFI_PASSWORD);

    if ((ssid_length == 0U) ||
        (ssid_length >= sizeof(wifi_config.sta.ssid)) ||
        (password_length >= sizeof(wifi_config.sta.password))) {
        ESP_LOGE(TAG, "Local Wi-Fi configuration length invalid");
        return false;
    }

    memcpy(
        wifi_config.sta.ssid,
        ESP_LOCAL_006_WIFI_SSID,
        ssid_length
    );

    memcpy(
        wifi_config.sta.password,
        ESP_LOCAL_006_WIFI_PASSWORD,
        password_length
    );

    wifi_config.sta.threshold.authmode = WIFI_AUTH_WPA2_PSK;

    err = esp_wifi_set_mode(WIFI_MODE_STA);

    if (err != ESP_OK) {
        ESP_LOGE(
            TAG,
            "esp_wifi_set_mode failed: %s",
            esp_err_to_name(err)
        );
        return false;
    }

    err = esp_wifi_set_config(
        WIFI_IF_STA,
        &wifi_config
    );

    if (err != ESP_OK) {
        ESP_LOGE(
            TAG,
            "esp_wifi_set_config failed: %s",
            esp_err_to_name(err)
        );
        return false;
    }

    err = esp_wifi_set_ps(WIFI_PS_NONE);

    if (err != ESP_OK) {
        ESP_LOGE(
            TAG,
            "esp_wifi_set_ps failed: %s",
            esp_err_to_name(err)
        );
        return false;
    }

    err = esp_wifi_start();

    if (err != ESP_OK) {
        ESP_LOGE(
            TAG,
            "esp_wifi_start failed: %s",
            esp_err_to_name(err)
        );
        return false;
    }

    EventBits_t bits = xEventGroupWaitBits(
        s_wifi_event_group,
        WIFI_CONNECTED_BIT | WIFI_FAIL_BIT,
        pdFALSE,
        pdFALSE,
        portMAX_DELAY
    );

    if ((bits & WIFI_CONNECTED_BIT) != 0U) {
        ESP_LOGI(TAG, "006_WIFI_CONNECTED");
        return true;
    }

    ESP_LOGE(TAG, "006_WIFI_CONNECT_FAILED");
    return false;
}


/* --------------------------------------------------------------------------
 * Application-layer listener
 * -------------------------------------------------------------------------- */

static void relay_listener_loop(void)
{
    while (true) {
        int server_sock = socket(
            AF_INET,
            SOCK_STREAM,
            IPPROTO_IP
        );

        if (server_sock < 0) {
            ESP_LOGE(
                TAG,
                "Unable to create listener socket: errno=%d",
                errno
            );
            vTaskDelay(pdMS_TO_TICKS(1000));
            continue;
        }

        int reuse = 1;

        (void)setsockopt(
            server_sock,
            SOL_SOCKET,
            SO_REUSEADDR,
            &reuse,
            sizeof(reuse)
        );

        struct sockaddr_in address = {
            .sin_family = AF_INET,
            .sin_port = htons(RELAY_LISTEN_PORT),
            .sin_addr.s_addr = htonl(INADDR_ANY)
        };

        if (bind(
                server_sock,
                (struct sockaddr *)&address,
                sizeof(address)
            ) != 0) {
            ESP_LOGE(
                TAG,
                "Listener bind failed: errno=%d",
                errno
            );
            close(server_sock);
            vTaskDelay(pdMS_TO_TICKS(1000));
            continue;
        }

        if (listen(server_sock, LISTEN_BACKLOG) != 0) {
            ESP_LOGE(
                TAG,
                "Listener listen failed: errno=%d",
                errno
            );
            close(server_sock);
            vTaskDelay(pdMS_TO_TICKS(1000));
            continue;
        }

        ESP_LOGI(
            TAG,
            "006_ENDPOINT_LISTENING port=%d",
            RELAY_LISTEN_PORT
        );

        while (true) {
            struct sockaddr_in source_address;
            socklen_t source_length = sizeof(source_address);

            int client_sock = accept(
                server_sock,
                (struct sockaddr *)&source_address,
                &source_length
            );

            if (client_sock < 0) {
                ESP_LOGE(
                    TAG,
                    "Listener accept failed: errno=%d",
                    errno
                );
                break;
            }

            char source_ip[INET_ADDRSTRLEN] = {0};

            inet_ntoa_r(
                source_address.sin_addr,
                source_ip,
                sizeof(source_ip)
            );

            ESP_LOGI(
                TAG,
                "006_REQUEST_FROM %s:%u",
                source_ip,
                (unsigned)ntohs(source_address.sin_port)
            );

            struct timeval timeout = {
                .tv_sec = 5,
                .tv_usec = 0
            };

            (void)setsockopt(
                client_sock,
                SOL_SOCKET,
                SO_RCVTIMEO,
                &timeout,
                sizeof(timeout)
            );

            (void)setsockopt(
                client_sock,
                SOL_SOCKET,
                SO_SNDTIMEO,
                &timeout,
                sizeof(timeout)
            );

            char line[MAX_REQUEST_LINE];

            if (!recv_request_line(
                    client_sock,
                    line,
                    sizeof(line)
                )) {
                ESP_LOGW(TAG, "006_DENY_REQUEST_READ");
                send_response(
                    client_sock,
                    false,
                    "request_read_failed"
                );
                close(client_sock);
                continue;
            }

            const char *denial_reason = process_request(line);

            if (denial_reason == NULL) {
                send_response(
                    client_sock,
                    true,
                    NULL
                );
            } else {
                send_response(
                    client_sock,
                    false,
                    denial_reason
                );
            }

            close(client_sock);
        }

        close(server_sock);
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}


/* --------------------------------------------------------------------------
 * app_main
 * -------------------------------------------------------------------------- */

void app_main(void)
{
    ESP_LOGI(
        TAG,
        "ESP-LOCAL-006 hostile-relay endpoint"
    );

    /*
     * Default NVS is required by Wi-Fi.
     * No erase/reinitialize fallback is allowed.
     */
    esp_err_t err = nvs_flash_init();

    if (err != ESP_OK) {
        ESP_LOGE(
            TAG,
            "Default NVS initialization failed: %s",
            esp_err_to_name(err)
        );
        ESP_LOGE(TAG, "006_STARTUP_FAIL_CLOSED");
        return;
    }

    /*
     * Dedicated authority partition.
     * Again: no erase/recovery fallback.
     */
    err = nvs_flash_init_partition(NUVL_PARTITION);

    if (err != ESP_OK) {
        ESP_LOGE(
            TAG,
            "Authority-state partition initialization failed: %s",
            esp_err_to_name(err)
        );
        ESP_LOGE(TAG, "006_STARTUP_FAIL_CLOSED");
        return;
    }

    psa_status_t psa_status = psa_crypto_init();

    if (psa_status != PSA_SUCCESS) {
        ESP_LOGE(
            TAG,
            "PSA crypto initialization failed: %ld",
            (long)psa_status
        );
        ESP_LOGE(TAG, "006_STARTUP_FAIL_CLOSED");
        return;
    }

    /*
     * Startup does not manufacture state.
     *
     * A structurally valid prior record may belong to another authority.
     * Exact authority-id matching happens after a signed request arrives.
     * Missing/corrupt state prevents the listener from starting.
     */
    nuvl_state_record_t startup_record;

    if (!load_state_record(&startup_record)) {
        ESP_LOGE(TAG, "006_STARTUP_STATE_INVALID_FAIL_CLOSED");
        return;
    }

    ESP_LOGI(
        TAG,
        "006_STARTUP_STATE_VALID state=%u",
        (unsigned)startup_record.state
    );

    if (!wifi_connect()) {
        ESP_LOGE(TAG, "006_STARTUP_WIFI_FAIL_CLOSED");
        return;
    }

    ESP_LOGI(TAG, "006_PROVIDER_PRIVATE_KEY=ABSENT");
    ESP_LOGI(TAG, "006_SIGNING_CAPABILITY=ABSENT");
    ESP_LOGI(TAG, "006_ENDPOINT_READY");

    relay_listener_loop();
}
