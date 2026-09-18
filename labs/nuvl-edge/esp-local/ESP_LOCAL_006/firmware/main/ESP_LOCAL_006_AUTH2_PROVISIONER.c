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
    uint8_t state;
    uint8_t reserved;
    uint8_t authority_id[NUVL_AUTHORITY_ID_LEN];
    uint32_t crc32;
} nuvl_state_record_t;

_Static_assert(sizeof(nuvl_state_record_t) == 44,
               "Unexpected nuvl_state_record_t size");

static const uint8_t EXPECTED_AUTHORITY_ID[NUVL_AUTHORITY_ID_LEN] = {
    0x19, 0x6a, 0x97, 0x3c, 0xfe, 0x65, 0xd8, 0x1c, 0x41, 0x56, 0x18, 0xf2, 0x87, 0x48, 0x74, 0xe6, 0x5d, 0x88, 0xe0, 0x06, 0x22, 0x37, 0x83, 0xbc, 0x07, 0x26, 0xa4, 0xc8, 0x4a, 0xcf, 0x87, 0xfc
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
    if (record == NULL) return false;
    if (record->magic != NUVL_STATE_MAGIC) return false;
    if (record->version != NUVL_STATE_VERSION) return false;
    if (record->reserved != 0U) return false;

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

    if (record->crc32 != record_crc(record)) return false;

    return true;
}

static void fail_closed(const char *stage, esp_err_t err)
{
    ESP_LOGE(TAG, "%s failed: %s",
             stage, esp_err_to_name(err));
    ESP_LOGE(TAG, "006_AUTH2_PROVISION_FAIL_CLOSED");
}

void app_main(void)
{
    esp_err_t err;
    nvs_handle_t handle;

    ESP_LOGI(TAG, "ESP-LOCAL-006 Authority #2 explicit provisioning");

    err = nvs_flash_init_partition(NUVL_NVS_PARTITION);
    if (err != ESP_OK) {
        fail_closed("nvs_flash_init_partition", err);
        return;
    }

    err = nvs_open_from_partition(
        NUVL_NVS_PARTITION,
        NUVL_NVS_NAMESPACE,
        NVS_READWRITE,
        &handle
    );

    if (err != ESP_OK) {
        fail_closed("nvs_open_from_partition", err);
        return;
    }

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
        ESP_LOGE(TAG,
                 "Existing authority state present; provisioning refused");
        ESP_LOGE(TAG, "006_AUTH2_PROVISION_FAIL_CLOSED");
        return;
    }

    if (err != ESP_ERR_NVS_NOT_FOUND) {
        nvs_close(handle);
        fail_closed("existing-state lookup", err);
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

    err = nvs_set_blob(
        handle,
        NUVL_NVS_STATE_KEY,
        &record,
        sizeof(record)
    );

    if (err != ESP_OK) {
        nvs_close(handle);
        fail_closed("nvs_set_blob", err);
        return;
    }

    err = nvs_commit(handle);

    if (err != ESP_OK) {
        nvs_close(handle);
        fail_closed("nvs_commit", err);
        return;
    }

    nvs_close(handle);

    err = nvs_flash_deinit_partition(NUVL_NVS_PARTITION);
    if (err != ESP_OK) {
        fail_closed("nvs_flash_deinit_partition", err);
        return;
    }

    err = nvs_flash_init_partition(NUVL_NVS_PARTITION);
    if (err != ESP_OK) {
        fail_closed("NVS reinitialization", err);
        return;
    }

    err = nvs_open_from_partition(
        NUVL_NVS_PARTITION,
        NUVL_NVS_NAMESPACE,
        NVS_READONLY,
        &handle
    );

    if (err != ESP_OK) {
        fail_closed("read-back open", err);
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
        fail_closed("read-back", err);
        return;
    }

    if (verify_len != sizeof(verify) ||
        !record_is_valid(&verify) ||
        verify.state != NUVL_AUTH_STATE_UNSPENT) {
        ESP_LOGE(TAG, "Authority #2 read-back validation failed");
        ESP_LOGE(TAG, "006_AUTH2_PROVISION_FAIL_CLOSED");
        return;
    }

    ESP_LOGI(
        TAG,
        "006_AUTH2_ID=196a973cfe65d81c415618f2874874e65d88e006223783bc0726a4c84acf87fc"
    );
    ESP_LOGI(TAG, "006_AUTH2_DURABLE_UNSPENT_VERIFIED");
    ESP_LOGI(TAG, "006_AUTH2_PROVISION_PASS");
}
