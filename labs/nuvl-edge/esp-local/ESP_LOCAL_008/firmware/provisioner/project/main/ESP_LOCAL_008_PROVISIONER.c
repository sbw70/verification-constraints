#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#include "esp_err.h"
#include "esp_log.h"
#include "nvs.h"
#include "nvs_flash.h"

static const char *TAG = "ESP_LOCAL_008";

/* --------------------------------------------------------------------------
 * ESP-LOCAL-008  -  explicit authority-state provisioner
 *
 * Writes ONE unspent authority-state record into the dedicated nuvl_state
 * partition, then durably reads it back and verifies it. Refuses to run if
 * any authority state is already present (fail-closed; no silent overwrite).
 *
 * Provisioning writes UNSPENT state. It does NOT spend an authority - the
 * signed authority artifact is separate and is only consumed by the endpoint
 * runtime when presented over the network.
 *
 * ENDPOINT_INSTANCE selects which frozen authority this board is armed with:
 *   1 -> Servo #1, identity esp32-xiao-servo-01, AUTH-X
 *        a1eb22c7b5530b644302f03c3d3a75ef5ebc115ecdca7028809f4cb1c5da104c
 *   2 -> Servo #2, identity esp32-xiao-servo-02, AUTH-Y
 *        5d2b8162de0923fcc08d39d7cf8715a37e25bf548c0344e802f3cfbc91b16fa9
 *
 * The instance MUST match the endpoint runtime flashed to the same board.
 * -------------------------------------------------------------------------- */

#define ENDPOINT_INSTANCE 1

#if ENDPOINT_INSTANCE == 1
#  define ENDPOINT_DEVICE_ID   "esp32-xiao-servo-01"
#  define AUTHORITY_LABEL      "AUTH-X3"
#  define AUTHORITY_ID_HEX \
       "5222af8445ee67ba8712f2469c91449a841c777cb40b9395d22c9bb1f30388ef"
#elif ENDPOINT_INSTANCE == 2
#  define ENDPOINT_DEVICE_ID   "esp32-xiao-servo-02"
#  define AUTHORITY_LABEL      "AUTH-Y2"
#  define AUTHORITY_ID_HEX \
       "3ba6239d703d5ba203be2069f1c4c3fc89c27e63cff0b59be6977883ca654519"
#else
#  error "ENDPOINT_INSTANCE must be 1 or 2"
#endif


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


#if ENDPOINT_INSTANCE == 1
static const uint8_t EXPECTED_AUTHORITY_ID[NUVL_AUTHORITY_ID_LEN] = {
    0x52, 0x22, 0xaf, 0x84, 0x45, 0xee, 0x67, 0xba,
    0x87, 0x12, 0xf2, 0x46, 0x9c, 0x91, 0x44, 0x9a,
    0x84, 0x1c, 0x77, 0x7c, 0xb4, 0x0b, 0x93, 0x95,
    0xd2, 0x2c, 0x9b, 0xb1, 0xf3, 0x03, 0x88, 0xef
};
#elif ENDPOINT_INSTANCE == 2
static const uint8_t EXPECTED_AUTHORITY_ID[NUVL_AUTHORITY_ID_LEN] = {
    0x3b, 0xa6, 0x23, 0x9d, 0x70, 0x3d, 0x5b, 0xa2,
    0x03, 0xbe, 0x20, 0x69, 0xf1, 0xc4, 0xc3, 0xfc,
    0x89, 0xc2, 0x7e, 0x63, 0xcf, 0xf0, 0xb5, 0x9b,
    0xe6, 0x97, 0x78, 0x83, 0xca, 0x65, 0x45, 0x19
};
#endif


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
    ESP_LOGE(TAG, "%s failed: %s", stage, esp_err_to_name(err));
    ESP_LOGE(TAG, "008_PROVISION_FAIL_CLOSED");
}

void app_main(void)
{
    esp_err_t err;
    nvs_handle_t handle;

    ESP_LOGI(TAG,
             "ESP-LOCAL-008 provisioning %s for %s",
             AUTHORITY_LABEL,
             ENDPOINT_DEVICE_ID);

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
        ESP_LOGE(TAG, "008_PROVISION_FAIL_CLOSED");
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
        ESP_LOGE(TAG, "%s read-back validation failed", AUTHORITY_LABEL);
        ESP_LOGE(TAG, "008_PROVISION_FAIL_CLOSED");
        return;
    }

    ESP_LOGI(TAG, "008_PROVISION_ENDPOINT=" ENDPOINT_DEVICE_ID);
    ESP_LOGI(TAG, "008_PROVISION_LABEL=" AUTHORITY_LABEL);
    ESP_LOGI(TAG, "008_AUTH_ID=" AUTHORITY_ID_HEX);
    ESP_LOGI(TAG, "008_DURABLE_UNSPENT_VERIFIED");
    ESP_LOGI(TAG, "008_PROVISION_PASS");
}
