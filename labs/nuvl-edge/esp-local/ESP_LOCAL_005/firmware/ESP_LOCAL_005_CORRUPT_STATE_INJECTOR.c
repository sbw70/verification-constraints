#include <stdint.h>
#include <string.h>

#include "esp_log.h"
#include "esp_err.h"
#include "nvs.h"
#include "nvs_flash.h"

#define NUVL_PARTITION          "nuvl_state"
#define NUVL_NAMESPACE          "nuvl_auth"
#define NUVL_STATE_KEY          "state"
#define NUVL_AUTHORITY_ID_LEN   32U

typedef struct {
    uint32_t magic;
    uint16_t version;
    uint8_t  state;
    uint8_t  reserved;
    uint8_t  authority_id[NUVL_AUTHORITY_ID_LEN];
    uint32_t crc32;
} nuvl_state_record_t;

static const char *TAG = "005_CORRUPT";

static const uint8_t AUTH3_ID[32] = {
    0x82,0xac,0xcb,0xc8,0xb1,0x09,0x92,0x49,
    0xdb,0xf8,0xc0,0xcd,0x43,0x8b,0xee,0x5b,
    0xe1,0xd9,0xf7,0x75,0x33,0xe5,0x48,0x18,
    0x89,0xdf,0xf9,0x18,0xa3,0xe6,0x9c,0x8d
};

void app_main(void)
{
    ESP_LOGI(TAG, "ESP-LOCAL-005 deliberate corrupt-state injector");

    esp_err_t err = nvs_flash_init_partition(NUVL_PARTITION);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "nvs init failed: %s", esp_err_to_name(err));
        return;
    }

    nvs_handle_t h;
    err = nvs_open_from_partition(
        NUVL_PARTITION,
        NUVL_NAMESPACE,
        NVS_READWRITE,
        &h
    );

    if (err != ESP_OK) {
        ESP_LOGE(TAG, "nvs open failed: %s", esp_err_to_name(err));
        return;
    }

    nuvl_state_record_t record;
    memset(&record, 0, sizeof(record));

    record.magic = 0xDEADBEEFU;  /* deliberately invalid */
    record.version = 1U;
    record.state = 2U;           /* SPENT */
    record.reserved = 0U;
    memcpy(record.authority_id, AUTH3_ID, sizeof(AUTH3_ID));
    record.crc32 = 0U;           /* deliberately invalid */

    ESP_LOGI(TAG, "Writing deliberately corrupt 44-byte state record");

    err = nvs_set_blob(h, NUVL_STATE_KEY, &record, sizeof(record));
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "nvs_set_blob failed: %s", esp_err_to_name(err));
        nvs_close(h);
        return;
    }

    err = nvs_commit(h);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "nvs_commit failed: %s", esp_err_to_name(err));
        nvs_close(h);
        return;
    }

    nvs_close(h);

    ESP_LOGI(TAG, "005_CORRUPT_STATE_COMMIT_PASS");
    ESP_LOGI(TAG, "Record is present but intentionally invalid");
}
