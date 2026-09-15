#include <stdint.h>
#include <string.h>

#include "esp_log.h"
#include "monocypher-ed25519.h"

static const char *TAG = "ESP_LOCAL_005";

/*
 * Frozen ESP-LOCAL-005 canonical authority.
 */
static const uint8_t CANONICAL_AUTHORITY[] =
    "{\"action\":\"move_servo\","
    "\"context\":\"esp_local_005\","
    "\"device_id\":\"esp32-xiao-servo-02\","
    "\"max_uses\":1,"
    "\"nonce\":\"bf00d0519a61597cf02e6a6520689664\"}";

/*
 * Frozen provider Ed25519 public key.
 */
static const uint8_t PROVIDER_PUBLIC_KEY[32] = {
    0x48, 0x85, 0x22, 0x70, 0xce, 0x16, 0x65, 0x4e,
    0xde, 0xef, 0x2a, 0x1c, 0x3d, 0x09, 0x30, 0xaf,
    0x4b, 0x99, 0x0e, 0x1b, 0xf5, 0x06, 0x0f, 0xb3,
    0x22, 0x19, 0x96, 0x43, 0x4f, 0x63, 0xe5, 0xb1
};

/*
 * Frozen provider signature over CANONICAL_AUTHORITY.
 *
 * Base64:
 * EMmSdyUABZwBGDuiqrNihoXeQ1AMuA2ugC4xZMKUaHGscvgLzn6qeRjl
 * +stq1IHQx9c3CoQw6MkoHpuEbmTMBQ==
 */
static const uint8_t PROVIDER_SIGNATURE[64] = {
    0x10, 0xc9, 0x92, 0x77, 0x25, 0x00, 0x05, 0x9c,
    0x01, 0x18, 0x3b, 0xa2, 0xaa, 0xb3, 0x62, 0x86,
    0x85, 0xde, 0x43, 0x50, 0x0c, 0xb8, 0x0d, 0xae,
    0x80, 0x2e, 0x31, 0x64, 0xc2, 0x94, 0x68, 0x71,
    0xac, 0x72, 0xf8, 0x0b, 0xce, 0x7e, 0xaa, 0x79,
    0x18, 0xe5, 0xfa, 0xcb, 0x6a, 0xd4, 0x81, 0xd0,
    0xc7, 0xd7, 0x37, 0x0a, 0x84, 0x30, 0xe8, 0xc9,
    0x28, 0x1e, 0x9b, 0x84, 0x6e, 0x64, 0xcc, 0x05
};

void app_main(void)
{
    int result;

    ESP_LOGI(TAG, "ESP-LOCAL-005 Monocypher Ed25519 capability gate");

    /*
     * CASE 1
     * Authentic provider key + authentic authority + authentic signature
     * must verify.
     *
     * crypto_ed25519_check():
     *   0  = valid
     *  -1  = invalid
     */
    result = crypto_ed25519_check(
        PROVIDER_SIGNATURE,
        PROVIDER_PUBLIC_KEY,
        CANONICAL_AUTHORITY,
        sizeof(CANONICAL_AUTHORITY) - 1
    );

    ESP_LOGI(TAG, "Authentic verification result=%d", result);

    if (result != 0) {
        ESP_LOGE(TAG, "Authentic provider signature rejected");
        ESP_LOGE(TAG, "005_MONOCYPHER_ED25519_GATE_FAIL");
        return;
    }

    ESP_LOGI(TAG, "005_MONOCYPHER_ED25519_VALID_PASS");

    /*
     * CASE 2
     * Change the signed authority while retaining the authentic
     * provider key and signature.
     */
    uint8_t tampered_authority[sizeof(CANONICAL_AUTHORITY)];

    memcpy(
        tampered_authority,
        CANONICAL_AUTHORITY,
        sizeof(CANONICAL_AUTHORITY)
    );

    char *action = strstr(
        (char *)tampered_authority,
        "move_servo"
    );

    if (action == NULL) {
        ESP_LOGE(TAG, "Internal authority-tamper setup failed");
        ESP_LOGE(TAG, "005_MONOCYPHER_ED25519_GATE_FAIL");
        return;
    }

    action[0] = 'n';

    result = crypto_ed25519_check(
        PROVIDER_SIGNATURE,
        PROVIDER_PUBLIC_KEY,
        tampered_authority,
        sizeof(CANONICAL_AUTHORITY) - 1
    );

    ESP_LOGI(TAG, "Tampered-authority verification result=%d", result);

    if (result == 0) {
        ESP_LOGE(TAG, "Tampered authority accepted");
        ESP_LOGE(TAG, "005_MONOCYPHER_ED25519_GATE_FAIL");
        return;
    }

    ESP_LOGI(TAG, "005_MONOCYPHER_ED25519_TAMPER_MESSAGE_PASS");

    /*
     * CASE 3
     * Change the signature while retaining the authentic provider key
     * and authentic authority.
     */
    uint8_t tampered_signature[sizeof(PROVIDER_SIGNATURE)];

    memcpy(
        tampered_signature,
        PROVIDER_SIGNATURE,
        sizeof(PROVIDER_SIGNATURE)
    );

    tampered_signature[0] ^= 0x01U;

    result = crypto_ed25519_check(
        tampered_signature,
        PROVIDER_PUBLIC_KEY,
        CANONICAL_AUTHORITY,
        sizeof(CANONICAL_AUTHORITY) - 1
    );

    ESP_LOGI(TAG, "Tampered-signature verification result=%d", result);

    if (result == 0) {
        ESP_LOGE(TAG, "Tampered signature accepted");
        ESP_LOGE(TAG, "005_MONOCYPHER_ED25519_GATE_FAIL");
        return;
    }

    ESP_LOGI(TAG, "005_MONOCYPHER_ED25519_TAMPER_SIGNATURE_PASS");
    ESP_LOGI(TAG, "005_MONOCYPHER_ED25519_GATE_PASS");
}
