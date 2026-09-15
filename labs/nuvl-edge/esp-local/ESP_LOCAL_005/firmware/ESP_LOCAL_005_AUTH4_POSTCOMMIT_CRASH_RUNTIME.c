#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

#include "esp_err.h"
#include "esp_log.h"

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#include "driver/gpio.h"
#include "driver/ledc.h"

#include "nvs.h"
#include "nvs_flash.h"

#include "monocypher-ed25519.h"

static const char *TAG = "ESP_LOCAL_005";

/* --------------------------------------------------------------------------
 * ESP-LOCAL-005
 *
 * Native-C endpoint-local persistent bounded-authority runtime.
 *
 * Evaluation order:
 *
 *   provider signature
 *       ->
 *   semantic admissibility
 *       ->
 *   persistent-state validity
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
 * or otherwise ambiguous persistent state never becomes fresh authority.
 *
 * No NVS auto-erase/recovery path exists in this runtime.
 * -------------------------------------------------------------------------- */


/* --------------------------------------------------------------------------
 * Hardware
 * -------------------------------------------------------------------------- */

#define TEST_TRIGGER_GPIO       GPIO_NUM_0
#define SERVO_GPIO              GPIO_NUM_5

#define SERVO_PWM_HZ            50
#define SERVO_HOLD_MS           1000

#define SERVO_LEDC_MODE         LEDC_LOW_SPEED_MODE
#define SERVO_LEDC_TIMER        LEDC_TIMER_0
#define SERVO_LEDC_CHANNEL      LEDC_CHANNEL_0
#define SERVO_LEDC_RESOLUTION   LEDC_TIMER_14_BIT

/*
 * 50 Hz = 20 ms period.
 * 2.0 ms high pulse = 10% duty.
 *
 * 14-bit full scale = 16384 counts.
 * 10% ~= 1638 counts.
 */
#define SERVO_DUTY_2MS          1638U


/* --------------------------------------------------------------------------
 * Persistent authority state
 * -------------------------------------------------------------------------- */

#define NUVL_STATE_MAGIC        0x4E55564CUL  /* "NUVL" */
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
 * Frozen ESP-LOCAL-005 provider authority
 * -------------------------------------------------------------------------- */

/*
 * Exact signed canonical authority:
 *
 * {"action":"move_servo","context":"esp_local_005",
 *  "device_id":"esp32-xiao-servo-02","max_uses":1,
 *  "nonce":"69bd5872bc3976545d246d966248c5ca"}
 *
 * Formatting above is explanatory only.
 * The byte string below is the exact canonical signed representation.
 */
static const uint8_t RECEIVED_AUTHORITY[] =
    "{\"action\":\"move_servo\","
    "\"context\":\"esp_local_005\","
    "\"device_id\":\"esp32-xiao-servo-02\","
    "\"max_uses\":1,"
    "\"nonce\":\"69bd5872bc3976545d246d966248c5ca\"}";

/*
 * Independently frozen admissible authority representation.
 * Runtime semantic admission requires exact byte equality.
 */
static const uint8_t EXPECTED_AUTHORITY[] =
    "{\"action\":\"move_servo\","
    "\"context\":\"esp_local_005\","
    "\"device_id\":\"esp32-xiao-servo-02\","
    "\"max_uses\":1,"
    "\"nonce\":\"69bd5872bc3976545d246d966248c5ca\"}";

/*
 * Provider Ed25519 public key.
 *
 * 48852270ce16654edeef2a1c3d0930af
 * 4b990e1bf5060fb3221996434f63e5b1
 */
static const uint8_t PROVIDER_PUBLIC_KEY[32] = {
    0x48, 0x85, 0x22, 0x70, 0xce, 0x16, 0x65, 0x4e,
    0xde, 0xef, 0x2a, 0x1c, 0x3d, 0x09, 0x30, 0xaf,
    0x4b, 0x99, 0x0e, 0x1b, 0xf5, 0x06, 0x0f, 0xb3,
    0x22, 0x19, 0x96, 0x43, 0x4f, 0x63, 0xe5, 0xb1
};

/*
 * Provider signature over RECEIVED_AUTHORITY.
 *
 * Base64:
 * BV1T7scFN4Ncy4fjiWxzQEugIAM3/BAGU6T/7B17pIxv6xPMxc8fwf51qNge
 * EcO3U8o0RyMsOSnjJnPetp+XDQ==
 */
static const uint8_t PROVIDER_SIGNATURE[64] = {
    0x05, 0x5d, 0x53, 0xee, 0xc7, 0x05, 0x37, 0x83,
    0x5c, 0xcb, 0x87, 0xe3, 0x89, 0x6c, 0x73, 0x40,
    0x4b, 0xa0, 0x20, 0x03, 0x37, 0xfc, 0x10, 0x06,
    0x53, 0xa4, 0xff, 0xec, 0x1d, 0x7b, 0xa4, 0x8c,
    0x6f, 0xeb, 0x13, 0xcc, 0xc5, 0xcf, 0x1f, 0xc1,
    0xfe, 0x75, 0xa8, 0xd8, 0x1e, 0x11, 0xc3, 0xb7,
    0x53, 0xca, 0x34, 0x47, 0x23, 0x2c, 0x39, 0x29,
    0xe3, 0x26, 0x73, 0xde, 0xb6, 0x9f, 0x97, 0x0d,
};

/*
 * SHA-256 of the exact canonical authority:
 *
 * 8da20bacde390ef6fbf278dc84490529
 * faaad24109f9ef53741bfb5f8ef0e86f
 */
static const uint8_t EXPECTED_AUTHORITY_ID[32] = {
    0x8d, 0xa2, 0x0b, 0xac, 0xde, 0x39, 0x0e, 0xf6,
    0xfb, 0xf2, 0x78, 0xdc, 0x84, 0x49, 0x05, 0x29,
    0xfa, 0xaa, 0xd2, 0x41, 0x09, 0xf9, 0xef, 0x53,
    0x74, 0x1b, 0xfb, 0x5f, 0x8e, 0xf0, 0xe8, 0x6f,
};


/* --------------------------------------------------------------------------
 * CRC32
 *
 * Same IEEE CRC32 used by the provisioning artifact.
 * Polynomial: 0xEDB88320
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

    if (memcmp(
            record->authority_id,
            EXPECTED_AUTHORITY_ID,
            sizeof(EXPECTED_AUTHORITY_ID)
        ) != 0) {
        ESP_LOGE(TAG, "Persistent authority ID mismatch");
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
    size_t required_size = 0;

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
 * Cryptographic recognition
 * -------------------------------------------------------------------------- */

static bool verify_provider_signature(void)
{
    int result = crypto_ed25519_check(
        PROVIDER_SIGNATURE,
        PROVIDER_PUBLIC_KEY,
        RECEIVED_AUTHORITY,
        sizeof(RECEIVED_AUTHORITY) - 1
    );

    if (result != 0) {
        ESP_LOGE(TAG, "Provider Ed25519 signature rejected");
        return false;
    }

    ESP_LOGI(TAG, "005_SIGNATURE_VALID");
    return true;
}


/* --------------------------------------------------------------------------
 * Semantic admissibility
 * -------------------------------------------------------------------------- */

static bool authority_is_admissible(void)
{
    if (sizeof(RECEIVED_AUTHORITY) != sizeof(EXPECTED_AUTHORITY)) {
        ESP_LOGE(TAG, "Authority semantic length mismatch");
        return false;
    }

    if (memcmp(
            RECEIVED_AUTHORITY,
            EXPECTED_AUTHORITY,
            sizeof(EXPECTED_AUTHORITY)
        ) != 0) {
        ESP_LOGE(TAG, "Authority outside configured admissibility");
        return false;
    }

    ESP_LOGI(TAG, "005_SEMANTIC_ADMISSIBILITY_PASS");
    return true;
}


/* --------------------------------------------------------------------------
 * Durable consumption
 *
 * The persistent state becomes SPENT and is committed before any PWM command.
 *
 * After commit:
 *   - close NVS
 *   - deinitialize the partition
 *   - reinitialize the partition
 *   - reopen
 *   - reread
 *   - validate
 *   - require SPENT
 *
 * No actuator command is issued unless this entire sequence succeeds.
 * -------------------------------------------------------------------------- */

static bool durable_consume(void)
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

    if (record.state != NUVL_AUTH_STATE_UNSPENT) {
        ESP_LOGE(TAG, "Authority is no longer UNSPENT");
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
            "Unable to stage SPENT authority state: %s",
            esp_err_to_name(err)
        );
        nvs_close(handle);
        return false;
    }

    err = nvs_commit(handle);

    if (err != ESP_OK) {
        ESP_LOGE(
            TAG,
            "Unable to commit SPENT authority state: %s",
            esp_err_to_name(err)
        );
        nvs_close(handle);
        return false;
    }

    nvs_close(handle);

    ESP_LOGI(TAG, "005_DURABLE_SPEND_COMMIT_PASS");

    /*
     * Force the verification path through a fresh partition initialization
     * rather than trusting the currently open NVS handle or cached record.
     */
    err = nvs_flash_deinit_partition(NUVL_PARTITION);

    if (err != ESP_OK) {
        ESP_LOGE(
            TAG,
            "Authority partition deinit failed after commit: %s",
            esp_err_to_name(err)
        );
        return false;
    }

    err = nvs_flash_init_partition(NUVL_PARTITION);

    if (err != ESP_OK) {
        ESP_LOGE(
            TAG,
            "Authority partition reinit failed after commit: %s",
            esp_err_to_name(err)
        );
        return false;
    }

    nuvl_state_record_t verified;

    if (!load_state_record(&verified)) {
        ESP_LOGE(TAG, "Committed authority state could not be verified");
        return false;
    }

    if (verified.state != NUVL_AUTH_STATE_SPENT) {
        ESP_LOGE(TAG, "Committed authority did not reread as SPENT");
        return false;
    }

    ESP_LOGI(TAG, "005_DURABLE_SPEND_READBACK_PASS");

    /*
     * ESP-LOCAL-005 fault injection:
     * authority is already durably SPENT and independently reread as SPENT.
     * Crash here before returning to the physical execution path.
     */
    ESP_LOGE(TAG, "005_FAULT_POST_COMMIT_PRE_PWM_ABORT");
    vTaskDelay(pdMS_TO_TICKS(100));
    abort();

    return false;
}


/* --------------------------------------------------------------------------
 * Physical execution
 * -------------------------------------------------------------------------- */

static bool issue_servo_command(void)
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
            "Servo PWM timer configuration failed: %s",
            esp_err_to_name(err)
        );
        return false;
    }

    ledc_channel_config_t channel_config = {
        .gpio_num       = SERVO_GPIO,
        .speed_mode     = SERVO_LEDC_MODE,
        .channel        = SERVO_LEDC_CHANNEL,
        .intr_type      = LEDC_INTR_DISABLE,
        .timer_sel      = SERVO_LEDC_TIMER,
        .duty           = 0,
        .hpoint         = 0,
        .flags.output_invert = 0
    };

    err = ledc_channel_config(&channel_config);

    if (err != ESP_OK) {
        ESP_LOGE(
            TAG,
            "Servo PWM channel configuration failed: %s",
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
            "Servo duty configuration failed: %s",
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
            "Servo duty update failed: %s",
            esp_err_to_name(err)
        );
        return false;
    }

    ESP_LOGI(TAG, "005_PWM_COMMAND_ISSUED");

    vTaskDelay(pdMS_TO_TICKS(SERVO_HOLD_MS));

    err = ledc_stop(
        SERVO_LEDC_MODE,
        SERVO_LEDC_CHANNEL,
        0
    );

    if (err != ESP_OK) {
        ESP_LOGE(
            TAG,
            "Servo PWM release failed: %s",
            esp_err_to_name(err)
        );

        /*
         * Authority is already durably spent.
         * Never restore authority because physical execution or release
         * became uncertain.
         */
        return false;
    }

    ESP_LOGI(TAG, "005_PWM_RELEASED");
    return true;
}


/* --------------------------------------------------------------------------
 * One authority evaluation
 * -------------------------------------------------------------------------- */

static void evaluate_authority(void)
{
    nuvl_state_record_t record;

    ESP_LOGI(TAG, "005_EVALUATION_BEGIN");

    /*
     * 1. Provider signature.
     */
    if (!verify_provider_signature()) {
        ESP_LOGE(TAG, "005_DENY_SIGNATURE");
        ESP_LOGE(TAG, "005_FAIL_CLOSED");
        return;
    }

    /*
     * 2. Configured semantic admissibility.
     */
    if (!authority_is_admissible()) {
        ESP_LOGE(TAG, "005_DENY_SEMANTICS");
        ESP_LOGE(TAG, "005_FAIL_CLOSED");
        return;
    }

    /*
     * 3. Persistent-state validity.
     */
    if (!load_state_record(&record)) {
        ESP_LOGE(TAG, "005_DENY_PERSISTENT_STATE_INVALID");
        ESP_LOGE(TAG, "005_FAIL_CLOSED");
        return;
    }

    /*
     * 4. Spent check.
     */
    if (record.state == NUVL_AUTH_STATE_SPENT) {
        ESP_LOGW(TAG, "005_REPLAY_DENIED_SPENT");
        return;
    }

    if (record.state != NUVL_AUTH_STATE_UNSPENT) {
        ESP_LOGE(TAG, "005_DENY_UNKNOWN_STATE");
        ESP_LOGE(TAG, "005_FAIL_CLOSED");
        return;
    }

    ESP_LOGI(TAG, "005_STATE_VALID_UNSPENT");

    /*
     * 5 + 6.
     * Durably consume, then independently reread SPENT.
     *
     * Nothing below this point executes unless persistence succeeds.
     */
    if (!durable_consume()) {
        ESP_LOGE(TAG, "005_DENY_DURABLE_CONSUME_FAILURE");
        ESP_LOGE(TAG, "005_FAIL_CLOSED");
        return;
    }

    /*
     * 7. Physical command only after durable SPENT verification.
     */
    if (!issue_servo_command()) {
        ESP_LOGE(TAG, "005_EXECUTION_AMBIGUOUS_AUTHORITY_REMAINS_SPENT");
        return;
    }

    ESP_LOGI(TAG, "005_EXECUTION_ACCEPTED");
}


/* --------------------------------------------------------------------------
 * Startup
 * -------------------------------------------------------------------------- */

static bool initialize_test_trigger(void)
{
    gpio_config_t config = {
        .pin_bit_mask = (1ULL << TEST_TRIGGER_GPIO),
        .mode         = GPIO_MODE_INPUT,
        .pull_up_en   = GPIO_PULLUP_ENABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type    = GPIO_INTR_DISABLE
    };

    esp_err_t err = gpio_config(&config);

    if (err != ESP_OK) {
        ESP_LOGE(
            TAG,
            "Test trigger GPIO configuration failed: %s",
            esp_err_to_name(err)
        );
        return false;
    }

    return true;
}


void app_main(void)
{
    ESP_LOGI(
        TAG,
        "ESP-LOCAL-005 native persistent-authority runtime"
    );

    ESP_LOGI(
        TAG,
        "Persistent record size: %u bytes",
        (unsigned)sizeof(nuvl_state_record_t)
    );

    /*
     * Dedicated authority partition only.
     *
     * Deliberately no:
     *   nvs_flash_erase()
     *   erase-on-init-error
     *   missing-state provisioning
     *   default UNSPENT construction
     */
    esp_err_t err = nvs_flash_init_partition(NUVL_PARTITION);

    if (err != ESP_OK) {
        ESP_LOGE(
            TAG,
            "Authority partition initialization failed: %s",
            esp_err_to_name(err)
        );

        ESP_LOGE(TAG, "005_STARTUP_FAIL_CLOSED");

        while (true) {
            vTaskDelay(pdMS_TO_TICKS(1000));
        }
    }

    /*
     * Startup validation is performed before accepting a trigger.
     */
    nuvl_state_record_t startup_record;

    if (!load_state_record(&startup_record)) {
        ESP_LOGE(TAG, "005_STARTUP_STATE_INVALID");
        ESP_LOGE(TAG, "005_STARTUP_FAIL_CLOSED");

        while (true) {
            vTaskDelay(pdMS_TO_TICKS(1000));
        }
    }

    if (startup_record.state == NUVL_AUTH_STATE_UNSPENT) {
        ESP_LOGI(TAG, "005_STARTUP_STATE_UNSPENT");
    } else if (startup_record.state == NUVL_AUTH_STATE_SPENT) {
        ESP_LOGI(TAG, "005_STARTUP_STATE_SPENT");
    } else {
        /*
         * validate_state_record() should already make this unreachable.
         */
        ESP_LOGE(TAG, "005_STARTUP_UNKNOWN_STATE");
        ESP_LOGE(TAG, "005_STARTUP_FAIL_CLOSED");

        while (true) {
            vTaskDelay(pdMS_TO_TICKS(1000));
        }
    }

    if (!initialize_test_trigger()) {
        ESP_LOGE(TAG, "005_STARTUP_TRIGGER_FAILURE");
        ESP_LOGE(TAG, "005_STARTUP_FAIL_CLOSED");

        while (true) {
            vTaskDelay(pdMS_TO_TICKS(1000));
        }
    }

    ESP_LOGI(
        TAG,
        "005_READY - press BOOT once to evaluate frozen authority"
    );

    /*
     * Rising runtime is deliberately inert until GPIO0 is pressed.
     * Flashing or attaching the monitor therefore does not consume the
     * provisioned one-use authority.
     */
    int previous_level = gpio_get_level(TEST_TRIGGER_GPIO);

    while (true) {
        int current_level = gpio_get_level(TEST_TRIGGER_GPIO);

        if ((previous_level == 1) && (current_level == 0)) {
            /*
             * Debounce.
             */
            vTaskDelay(pdMS_TO_TICKS(50));

            if (gpio_get_level(TEST_TRIGGER_GPIO) == 0) {
                evaluate_authority();

                /*
                 * Require release before another evaluation.
                 */
                while (gpio_get_level(TEST_TRIGGER_GPIO) == 0) {
                    vTaskDelay(pdMS_TO_TICKS(20));
                }

                ESP_LOGI(
                    TAG,
                    "005_READY - press BOOT to evaluate again"
                );
            }

            previous_level = 1;
            continue;
        }

        previous_level = current_level;

        vTaskDelay(pdMS_TO_TICKS(20));
    }
}
