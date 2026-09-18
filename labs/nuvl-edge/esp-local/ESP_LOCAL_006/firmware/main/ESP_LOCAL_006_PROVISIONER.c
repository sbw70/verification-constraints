#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#include "esp_err.h"
#include "esp_log.h"
#include "nvs.h"
#include "nvs_flash.h"

static const char *TAG = "ESP_LOCAL_006";

#define NUVL_STATE_MAGIC        0x4E55564CUL
#define NUVL_STATE_VERSION      1U

#define NUVL_NVS_PARTITION      "nuvl_state"
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
    "Unexpected nuvl_state_record_t size"
);

/*
 * ESP-LOCAL-006 Authority #1
 *
 * Exact canonical authority:
 *
 * {"action":"move_servo","context":"esp_local_006","device_id":"esp32-xiao-servo-02","max_uses":1,"nonce":"99337255d93cee60019493a813c42f23"}
 *
 * SHA-256:
 * f72ade66cea3c93c2cb57944e03d69e185a061a59f83c3705a8e6977dfddc7d6
 */
static const uint8_t EXPECTED_AUTHORITY_ID[NUVL_AUTHORITY_ID_LEN] = {
    0xf7, 0x2a, 0xde, 0x66, 0xce, 0xa3, 0xc9, 0x3c, 0x2c, 0xb5, 0x79, 0x44, 0xe0, 0x3d, 0x69, 0xe1, 0x85, 0xa0, 0x61, 0xa5, 0x9f, 0x83, 0xc3, 0x70, 0x5a, 0x8e, 0x69, 0x77, 0xdf, 0xdd, 0xc7, 0xd6
};

static uint32_t crc32_ieee(const void *data, size_t len)
{
    const uint8_t *p = (const uint8_t *)data;
    uint32_t crc = 0xFFFFFFFFU;

    for (size_t i = 0; i < len; ++i) {
        crc ^= p[i];

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

static uint32_t record_crc(const nuvl_state_record_t *record)
{
    return crc32_ieee(
        record,
        offsetof(nuvl_state_record_t, crc32)
    );
}

static bool record_is_valid(const nuvl_state_record_t *record)
{
    if (record == NULL) {
        return false;
    }

    if (record->magic != NUVL_STATE_MAGIC) {
        return false;
    }

    if (record->version != NUVL_STATE_VERSION) {
        return false;
    }

    if (record->reserved != 0U) {
        return false;
    }

    if ((record->state != NUVL_AUTH_STATE_UNSPENT) &&
        (record->state != NUVL_AUTH_STATE_SPENT)) {
        return false;
    }

    if (memcmp(
            record->authority_id,
            EXPECTED_AUTHORITY_ID,
            NUVL_AUTHORITY_ID_LEN
        ) != 0) {
        return false;
    }

    if (record->crc32 != record_crc(record)) {
        return false;
    }

    return true;
}

static void log_fail(const char *stage, esp_err_t err)
{
    ESP_LOGE(
        TAG,
        "%s failed: %s",
        stage,
        esp_err_to_name(err)
    );
    ESP_LOGE(TAG, "006_PROVISION_FAIL_CLOSED");
}

void app_main(void)
{
    esp_err_t err;
    nvs_handle_t handle;

    ESP_LOGI(
        TAG,
        "ESP-LOCAL-006 Authority #1 explicit provisioning"
    );

    err = nvs_flash_init_partition(NUVL_NVS_PARTITION);

    if (err != ESP_OK) {
        log_fail("nvs_flash_init_partition", err);
        return;
    }

    err = nvs_open_from_partition(
        NUVL_NVS_PARTITION,
        NUVL_NVS_NAMESPACE,
        NVS_READWRITE,
        &handle
    );

    if (err != ESP_OK) {
        log_fail("nvs_open_from_partition", err);
        return;
    }

    /*
     * Never overwrite existing authority state.
     *
     * Reuse of an old SPENT or UNSPENT record is not interpreted as
     * authorization to provision a new authority.
     */
    nuvl_state_record_t existing;
    size_t existing_len = sizeof(existing);

    err = nvs_get_blob(
        handle,
        NUVL_NVS_STATE_KEY,
        &existing,
        &existing_len
    );

    if (err == ESP_OK) {
        nvs_close(handle);

        ESP_LOGE(
            TAG,
            "Existing authority state present; provisioning refused"
        );
        ESP_LOGE(TAG, "006_PROVISION_FAIL_CLOSED");
        return;
    }

    if (err != ESP_ERR_NVS_NOT_FOUND) {
        nvs_close(handle);
        log_fail("existing-state lookup", err);
        return;
    }

    nuvl_state_record_t record;
    memset(&record, 0, sizeof(record));

    record.magic = NUVL_STATE_MAGIC;
    record.version = NUVL_STATE_VERSION;
    record.state = NUVL_AUTH_STATE_UNSPENT;
    record.reserved = 0U;

    memcpy(
        record.authority_id,
        EXPECTED_AUTHORITY_ID,
        NUVL_AUTHORITY_ID_LEN
    );

    record.crc32 = record_crc(&record);

    ESP_LOGI(
        TAG,
        "Writing explicit Authority #1 UNSPENT state"
    );

    err = nvs_set_blob(
        handle,
        NUVL_NVS_STATE_KEY,
        &record,
        sizeof(record)
    );

    if (err != ESP_OK) {
        nvs_close(handle);
        log_fail("nvs_set_blob", err);
        return;
    }

    err = nvs_commit(handle);

    if (err != ESP_OK) {
        nvs_close(handle);
        log_fail("nvs_commit", err);
        return;
    }

    nvs_close(handle);

    /*
     * Force a fresh NVS load before declaring provisioning successful.
     */
    err = nvs_flash_deinit_partition(NUVL_NVS_PARTITION);

    if (err != ESP_OK) {
        log_fail("nvs_flash_deinit_partition", err);
        return;
    }

    err = nvs_flash_init_partition(NUVL_NVS_PARTITION);

    if (err != ESP_OK) {
        log_fail("NVS reinitialization", err);
        return;
    }

    err = nvs_open_from_partition(
        NUVL_NVS_PARTITION,
        NUVL_NVS_NAMESPACE,
        NVS_READONLY,
        &handle
    );

    if (err != ESP_OK) {
        log_fail("read-back open", err);
        return;
    }

    nuvl_state_record_t verify;
    size_t verify_len = sizeof(verify);

    err = nvs_get_blob(
        handle,
        NUVL_NVS_STATE_KEY,
        &verify,
        &verify_len
    );

    nvs_close(handle);

    if (err != ESP_OK) {
        log_fail("read-back", err);
        return;
    }

    if (verify_len != sizeof(verify)) {
        ESP_LOGE(TAG, "Read-back record length invalid");
        ESP_LOGE(TAG, "006_PROVISION_FAIL_CLOSED");
        return;
    }

    if (!record_is_valid(&verify)) {
        ESP_LOGE(
            TAG,
            "Read-back authority record validation failed"
        );
        ESP_LOGE(TAG, "006_PROVISION_FAIL_CLOSED");
        return;
    }

    if (verify.state != NUVL_AUTH_STATE_UNSPENT) {
        ESP_LOGE(TAG, "Read-back state is not UNSPENT");
        ESP_LOGE(TAG, "006_PROVISION_FAIL_CLOSED");
        return;
    }

    ESP_LOGI(
        TAG,
        "006_AUTHORITY_ID=f72ade66cea3c93c2cb57944e03d69e185a061a59f83c3705a8e6977dfddc7d6"
    );
    ESP_LOGI(TAG, "006_DURABLE_UNSPENT_VERIFIED");
    ESP_LOGI(TAG, "006_PROVISION_UNSPENT_PASS");
}
