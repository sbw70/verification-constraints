#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "esp_err.h"
#include "esp_log.h"
#include "nvs.h"
#include "nvs_flash.h"

static const char *TAG = "ESP_LOCAL_005";

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

_Static_assert(sizeof(nuvl_state_record_t) == 44,
               "Unexpected nuvl_state_record_t size");

/*
 * Frozen ESP-LOCAL-005 authority_id:
 *
 * SHA256(
 * {"action":"move_servo","context":"esp_local_005",
 *  "device_id":"esp32-xiao-servo-02","max_uses":1,
 *  "nonce":"bf00d0519a61597cf02e6a6520689664"}
 * )
 *
 * b0726ba4fd440577313bc91c966f20e3
 * 84fa1daaa75b0a3e21b688d6039500b3
 */
static const uint8_t EXPECTED_AUTHORITY_ID[NUVL_AUTHORITY_ID_LEN] = {
    0xb0, 0x72, 0x6b, 0xa4, 0xfd, 0x44, 0x05, 0x77,
    0x31, 0x3b, 0xc9, 0x1c, 0x96, 0x6f, 0x20, 0xe3,
    0x84, 0xfa, 0x1d, 0xaa, 0xa7, 0x5b, 0x0a, 0x3e,
    0x21, 0xb6, 0x88, 0xd6, 0x03, 0x95, 0x00, 0xb3,
};

static uint32_t crc32_ieee(const void *data, size_t len)
{
    const uint8_t *p = (const uint8_t *)data;
    uint32_t crc = 0xFFFFFFFFU;

    for (size_t i = 0; i < len; ++i) {
        crc ^= p[i];

        for (unsigned bit = 0; bit < 8; ++bit) {
            if (crc & 1U) {
                crc = (crc >> 1) ^ 0xEDB88320U;
            } else {
                crc >>= 1;
            }
        }
    }

    return crc ^ 0xFFFFFFFFU;
}

static uint32_t record_crc(const nuvl_state_record_t *record)
{
    return crc32_ieee(record,
                      offsetof(nuvl_state_record_t, crc32));
}

static bool record_is_valid(const nuvl_state_record_t *record)
{
    if (record->magic != NUVL_STATE_MAGIC) {
        return false;
    }

    if (record->version != NUVL_STATE_VERSION) {
        return false;
    }

    if (record->reserved != 0U) {
        return false;
    }

    if (record->state != NUVL_AUTH_STATE_UNSPENT &&
        record->state != NUVL_AUTH_STATE_SPENT) {
        return false;
    }

    if (memcmp(record->authority_id,
               EXPECTED_AUTHORITY_ID,
               NUVL_AUTHORITY_ID_LEN) != 0) {
        return false;
    }

    if (record->crc32 != record_crc(record)) {
        return false;
    }

    return true;
}

static void log_fail(const char *stage, esp_err_t err)
{
    ESP_LOGE(TAG, "%s failed: %s",
             stage, esp_err_to_name(err));
    ESP_LOGE(TAG, "FAIL_CLOSED");
}

void app_main(void)
{
    esp_err_t err;
    nvs_handle_t handle;

    ESP_LOGI(TAG, "ESP-LOCAL-005 explicit provisioning");
    ESP_LOGI(TAG, "Initializing %s", NUVL_NVS_PARTITION);

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

        if (existing_len != sizeof(existing) ||
            !record_is_valid(&existing)) {
            ESP_LOGE(TAG,
                     "Existing authority state is invalid");
            ESP_LOGE(TAG, "FAIL_CLOSED");
            return;
        }

        ESP_LOGE(TAG,
                 "Existing valid authority state already present");
        ESP_LOGE(TAG,
                 "Provisioning refused; state=%u",
                 (unsigned int)existing.state);
        ESP_LOGE(TAG, "FAIL_CLOSED");
        return;
    }

    if (err != ESP_ERR_NVS_NOT_FOUND) {
        nvs_close(handle);
        log_fail("existing-state lookup", err);
        return;
    }

    /*
     * Explicit first provisioning only.
     */
    nuvl_state_record_t record;
    memset(&record, 0, sizeof(record));

    record.magic = NUVL_STATE_MAGIC;
    record.version = NUVL_STATE_VERSION;
    record.state = NUVL_AUTH_STATE_UNSPENT;
    record.reserved = 0U;

    memcpy(record.authority_id,
           EXPECTED_AUTHORITY_ID,
           NUVL_AUTHORITY_ID_LEN);

    record.crc32 = record_crc(&record);

    ESP_LOGI(TAG, "Writing explicit UNSPENT authority state");

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

    ESP_LOGI(TAG, "Committing authority state");

    err = nvs_commit(handle);

    if (err != ESP_OK) {
        nvs_close(handle);
        log_fail("nvs_commit", err);
        return;
    }

    nvs_close(handle);

    /*
     * Force a fresh NVS load before verification.
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
        ESP_LOGE(TAG,
                 "Read-back record length invalid: %u",
                 (unsigned int)verify_len);
        ESP_LOGE(TAG, "FAIL_CLOSED");
        return;
    }

    if (!record_is_valid(&verify)) {
        ESP_LOGE(TAG,
                 "Read-back authority record validation failed");
        ESP_LOGE(TAG, "FAIL_CLOSED");
        return;
    }

    if (verify.state != NUVL_AUTH_STATE_UNSPENT) {
        ESP_LOGE(TAG,
                 "Read-back state is not UNSPENT");
        ESP_LOGE(TAG, "FAIL_CLOSED");
        return;
    }

    ESP_LOGI(TAG, "Durable UNSPENT record verified");
    ESP_LOGI(TAG, "005_PROVISION_UNSPENT_PASS");
}
