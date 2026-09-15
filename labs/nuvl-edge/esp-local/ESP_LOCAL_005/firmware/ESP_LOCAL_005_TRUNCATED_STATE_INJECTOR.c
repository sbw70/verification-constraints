#include <stdint.h>

#include "esp_log.h"
#include "esp_err.h"
#include "nvs.h"
#include "nvs_flash.h"

#define NUVL_PARTITION "nuvl_state"
#define NUVL_NAMESPACE "nuvl_auth"
#define NUVL_STATE_KEY "state"

static const char *TAG = "005_TRUNCATE";

void app_main(void)
{
    ESP_LOGI(TAG, "ESP-LOCAL-005 deliberate truncated-state injector");

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

    static const uint8_t truncated_record[12] = {
        0x4c, 0x56, 0x55, 0x4e,
        0x01, 0x00,
        0x02,
        0x00,
        0x82, 0xac, 0xcb, 0xc8
    };

    ESP_LOGI(TAG, "Writing deliberately truncated state blob: 12 bytes");

    err = nvs_set_blob(
        h,
        NUVL_STATE_KEY,
        truncated_record,
        sizeof(truncated_record)
    );

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

    ESP_LOGI(TAG, "005_TRUNCATED_STATE_COMMIT_PASS");
}
