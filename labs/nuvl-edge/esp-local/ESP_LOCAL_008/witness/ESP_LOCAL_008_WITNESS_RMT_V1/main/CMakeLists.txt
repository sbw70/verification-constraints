idf_component_register(
    SRCS
        "witness_rmt_v1.c"
        "cJSON.c"
    INCLUDE_DIRS "."
    REQUIRES
        esp_driver_rmt
        esp_driver_gpio
        esp_driver_ledc
        esp_wifi
        esp_event
        esp_netif
        esp_timer
        nvs_flash
        spiffs
        mbedtls
        lwip
)


