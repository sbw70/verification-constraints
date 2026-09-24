#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include <stdbool.h>
#include <stdint.h>
#include <inttypes.h>
#include <errno.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <arpa/inet.h>

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"
#include "freertos/semphr.h"

#include "driver/gpio.h"
#include "driver/rmt_rx.h"
#include "driver/rmt_tx.h"
#include "driver/rmt_encoder.h"
#include "driver/ledc.h"
#include "esp_rom_sys.h"

#include "esp_attr.h"
#include "esp_err.h"
#include "esp_event.h"
#include "esp_log.h"
#include "esp_mac.h"
#include "esp_netif.h"
#include "esp_spiffs.h"
#include "esp_timer.h"
#include "esp_wifi.h"

#include "nvs.h"
#include "nvs_flash.h"
#include "psa/crypto.h"
#include "cJSON.h"

#include "witness_wifi_config.h"

#define DEVICE_ID               "esp32-witness-007"
#define CONTROL_MAGIC           "W007"
#define CONTROL_PORT            19072
#define WITNESS_GPIO            GPIO_NUM_4
#define SELFTEST_GPIO            GPIO_NUM_6
#define SELFTEST_PULSES          50

#define SERVO_MIN_US            1500
#define SERVO_MAX_US            2500
#define PERIOD_MIN_US           15000
#define PERIOD_MAX_US           25000
#define BURST_GAP_US            100000
#define RUN_START_QUIET_US      250000
#define STOP_QUIET_TIMEOUT_MS   1500

#define RMT_RESOLUTION_HZ       1000000
#define RX_IDLE_STOP_US         30000
#define RX_SIGNAL_MIN_NS        1250
#define RX_SIGNAL_MAX_NS        (RX_IDLE_STOP_US * 1000)
#define RX_BUFFER_SYMBOLS       256
#define CAPTURE_QUEUE_DEPTH     4

#define MAX_RUN_ID_LEN          20
#define EVIDENCE_BASE           "/evidence"
#define EVIDENCE_PARTITION      "evidence"

#define SESSION_NAME_MAX        96
#define RUN_NAME_MAX            160
#define IP_STRING_MAX           16

static const char *TAG = "W007_RMT_WITNESS";

static SemaphoreHandle_t state_mutex;
static QueueHandle_t rmt_done_queue;
static QueueHandle_t capture_queue;
static rmt_channel_handle_t rx_channel;
static rmt_channel_handle_t selftest_tx_channel;
static rmt_encoder_handle_t selftest_copy_encoder;

static FILE *session_file;
static FILE *run_file;
static bool storage_ready;
static bool rmt_ready;
static volatile bool udp_ready;

static uint32_t boot_counter;
static uint32_t event_seq;
static uint32_t pulse_seq;
static uint32_t burst_seq;
static char uid_short[9];
static char session_id[96];
static char session_basename[SESSION_NAME_MAX];
static char session_path[RUN_NAME_MAX];

static char active_run[MAX_RUN_ID_LEN + 1];
static char active_run_anchor[64];
static char active_run_basename[RUN_NAME_MAX];
static char active_run_path[RUN_NAME_MAX];
static int64_t run_start_us;

static uint32_t run_servo_valid_pulses;
static uint32_t run_transients;
static uint32_t run_bursts;
static uint32_t run_servo_like_bursts;
static uint32_t run_capture_overflows_start;
static uint32_t run_capture_truncations_start;
static uint32_t run_capture_errors_start;

static uint32_t capture_overflows;
static uint32_t capture_truncations;
static uint32_t capture_errors;
static int64_t last_edge_us;

static bool burst_active;
static char burst_run[MAX_RUN_ID_LEN + 1];
static int64_t burst_first_rise_us;
static int64_t burst_last_rise_us;
static int64_t burst_last_end_us;
static uint32_t burst_pulses;
static uint32_t burst_width_min;
static uint32_t burst_width_max;
static uint64_t burst_width_sum;
static uint32_t burst_period_min;
static uint32_t burst_period_max;
static uint32_t burst_period_bad;
static int64_t last_valid_rise_us;

static volatile bool wifi_connected;
static bool wifi_configured;
static char current_ip[IP_STRING_MAX] = "0.0.0.0";
static char configured_ssid[33];

static bool last_reported_wifi;
static uint32_t last_reported_overflows;
static uint32_t last_reported_truncations;
static uint32_t last_reported_errors;


typedef struct {
    size_t num_symbols;
    int64_t done_us;
    rmt_symbol_word_t symbols[RX_BUFFER_SYMBOLS];
} capture_block_t;


static void lock_state(void)
{
    xSemaphoreTake(state_mutex, portMAX_DELAY);
}

static void unlock_state(void)
{
    xSemaphoreGive(state_mutex);
}

static void sync_file(FILE *f)
{
    if (!f) {
        return;
    }
    fflush(f);
    int fd = fileno(f);
    if (fd >= 0) {
        fsync(fd);
    }
}

static cJSON *new_event(const char *type)
{
    cJSON *obj = cJSON_CreateObject();
    if (!obj) {
        return NULL;
    }
    cJSON_AddStringToObject(obj, "type", type);
    return obj;
}

static void write_event(cJSON *obj)
{
    if (!obj) {
        return;
    }

    lock_state();

    event_seq++;
    cJSON_AddNumberToObject(obj, "event_seq", event_seq);
    cJSON_AddStringToObject(obj, "device_id", DEVICE_ID);
    cJSON_AddStringToObject(obj, "session", session_id);
    cJSON_AddNumberToObject(obj, "boot", boot_counter);
    cJSON_AddNumberToObject(obj, "t_us", (double)esp_timer_get_time());
    cJSON_AddStringToObject(obj, "run", active_run[0] ? active_run : "NONE");

    char *line = cJSON_PrintUnformatted(obj);
    if (line) {
        printf("%s\n", line);

        if (session_file) {
            fprintf(session_file, "%s\n", line);
            fflush(session_file);
        }
        if (run_file) {
            fprintf(run_file, "%s\n", line);
            fflush(run_file);
        }

        free(line);
    }

    unlock_state();
    cJSON_Delete(obj);
}

static bool sha256_file(const char *path, char hex_out[65])
{
    FILE *f = fopen(path, "rb");
    if (!f) {
        return false;
    }

    psa_hash_operation_t op = PSA_HASH_OPERATION_INIT;
    psa_status_t status = psa_hash_setup(&op, PSA_ALG_SHA_256);
    if (status != PSA_SUCCESS) {
        fclose(f);
        return false;
    }

    uint8_t buf[1024];
    size_t n;
    while ((n = fread(buf, 1, sizeof(buf), f)) > 0) {
        status = psa_hash_update(&op, buf, n);
        if (status != PSA_SUCCESS) {
            psa_hash_abort(&op);
            fclose(f);
            return false;
        }
    }
    fclose(f);

    uint8_t digest[PSA_HASH_LENGTH(PSA_ALG_SHA_256)];
    size_t digest_len = 0;
    status = psa_hash_finish(&op, digest, sizeof(digest), &digest_len);
    if (status != PSA_SUCCESS || digest_len != 32) {
        psa_hash_abort(&op);
        return false;
    }

    for (size_t i = 0; i < digest_len; ++i) {
        snprintf(hex_out + (i * 2), 3, "%02x", digest[i]);
    }
    hex_out[64] = '\0';
    return true;
}

static bool valid_run_name(const char *name)
{
    if (!name || !name[0]) {
        return false;
    }
    size_t len = strlen(name);
    if (len > MAX_RUN_ID_LEN) {
        return false;
    }
    for (size_t i = 0; i < len; ++i) {
        char c = name[i];
        bool ok = ((c >= '0' && c <= '9') ||
                   (c >= 'A' && c <= 'Z') ||
                   (c >= 'a' && c <= 'z') ||
                   c == '-' || c == '_');
        if (!ok) {
            return false;
        }
    }
    return true;
}

static uint32_t next_boot_counter(bool nvs_ok)
{
    if (!nvs_ok) {
        return 1;
    }

    nvs_handle_t h;
    if (nvs_open("w007_meta", NVS_READWRITE, &h) != ESP_OK) {
        return 1;
    }

    uint32_t previous = 0;
    esp_err_t err = nvs_get_u32(h, "boot_count", &previous);
    if (err != ESP_OK && err != ESP_ERR_NVS_NOT_FOUND) {
        nvs_close(h);
        return 1;
    }

    uint32_t current = previous + 1;
    if (nvs_set_u32(h, "boot_count", current) == ESP_OK) {
        nvs_commit(h);
    }
    nvs_close(h);
    return current;
}

static bool mount_evidence_storage(void)
{
    esp_vfs_spiffs_conf_t conf = {
        .base_path = EVIDENCE_BASE,
        .partition_label = EVIDENCE_PARTITION,
        .max_files = 8,
        .format_if_mount_failed = true,
    };

    esp_err_t err = esp_vfs_spiffs_register(&conf);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "SPIFFS mount failed: %s", esp_err_to_name(err));
        return false;
    }

    size_t total = 0;
    size_t used = 0;
    err = esp_spiffs_info(EVIDENCE_PARTITION, &total, &used);
    if (err == ESP_OK) {
        printf("W007_EVIDENCE_STORAGE total=%u used=%u\n",
               (unsigned)total, (unsigned)used);
    }
    return true;
}

static void reset_burst_state(void)
{
    burst_active = false;
    burst_run[0] = '\0';
    burst_first_rise_us = 0;
    burst_last_rise_us = 0;
    burst_last_end_us = 0;
    burst_pulses = 0;
    burst_width_min = 0;
    burst_width_max = 0;
    burst_width_sum = 0;
    burst_period_min = 0;
    burst_period_max = 0;
    burst_period_bad = 0;
}

static void close_burst(const char *reason)
{
    if (!burst_active) {
        return;
    }

    bool servo_like = (burst_pulses >= 3 && burst_period_bad == 0);
    uint32_t width_mean = burst_pulses ? (uint32_t)(burst_width_sum / burst_pulses) : 0;
    int64_t duration_us = burst_last_end_us - burst_first_rise_us;

    lock_state();
    if (burst_run[0] && active_run[0] && strcmp(burst_run, active_run) == 0) {
        run_bursts++;
        if (servo_like) {
            run_servo_like_bursts++;
        }
    }
    unlock_state();

    cJSON *obj = new_event("burst_end");
    if (obj) {
        cJSON_AddNumberToObject(obj, "burst", burst_seq);
        cJSON_AddStringToObject(obj, "burst_run", burst_run[0] ? burst_run : "NONE");
        cJSON_AddStringToObject(obj, "reason", reason);
        cJSON_AddNumberToObject(obj, "first_rise_us", (double)burst_first_rise_us);
        cJSON_AddNumberToObject(obj, "last_rise_us", (double)burst_last_rise_us);
        cJSON_AddNumberToObject(obj, "last_end_us", (double)burst_last_end_us);
        cJSON_AddNumberToObject(obj, "duration_us", (double)duration_us);
        cJSON_AddNumberToObject(obj, "pulses", burst_pulses);
        cJSON_AddNumberToObject(obj, "width_min_us", burst_width_min);
        cJSON_AddNumberToObject(obj, "width_max_us", burst_width_max);
        cJSON_AddNumberToObject(obj, "width_mean_us", width_mean);
        if (burst_period_min) {
            cJSON_AddNumberToObject(obj, "period_min_us", burst_period_min);
            cJSON_AddNumberToObject(obj, "period_max_us", burst_period_max);
        } else {
            cJSON_AddNullToObject(obj, "period_min_us");
            cJSON_AddNullToObject(obj, "period_max_us");
        }
        cJSON_AddNumberToObject(obj, "period_out_of_range", burst_period_bad);
        cJSON_AddBoolToObject(obj, "servo_like", servo_like);
        write_event(obj);
    }

    reset_burst_state();
}

static void begin_burst(int64_t rise_us, int64_t end_us, uint32_t width_us)
{
    lock_state();
    burst_seq++;
    uint32_t this_burst = burst_seq;
    snprintf(burst_run, sizeof(burst_run), "%s", active_run);
    unlock_state();

    burst_active = true;
    burst_first_rise_us = rise_us;
    burst_last_rise_us = rise_us;
    burst_last_end_us = end_us;
    burst_pulses = 1;
    burst_width_min = width_us;
    burst_width_max = width_us;
    burst_width_sum = width_us;
    burst_period_min = 0;
    burst_period_max = 0;
    burst_period_bad = 0;

    cJSON *obj = new_event("burst_start");
    if (obj) {
        cJSON_AddNumberToObject(obj, "burst", this_burst);
        cJSON_AddStringToObject(obj, "burst_run", burst_run[0] ? burst_run : "NONE");
        cJSON_AddNumberToObject(obj, "first_rise_us", (double)rise_us);
        cJSON_AddNumberToObject(obj, "first_width_us", width_us);
        write_event(obj);
    }
}

static int64_t add_valid_pulse(int64_t rise_us, int64_t end_us, uint32_t width_us)
{
    int64_t period_us = -1;

    if (burst_active) {
        int64_t gap_us = rise_us - burst_last_rise_us;
        if (gap_us >= BURST_GAP_US) {
            close_burst("gap");
            begin_burst(rise_us, end_us, width_us);
        } else {
            if (last_valid_rise_us > 0) {
                period_us = rise_us - last_valid_rise_us;
            }

            burst_pulses++;
            burst_last_rise_us = rise_us;
            burst_last_end_us = end_us;
            burst_width_sum += width_us;
            if (width_us < burst_width_min) burst_width_min = width_us;
            if (width_us > burst_width_max) burst_width_max = width_us;

            if (period_us >= 0) {
                uint32_t p = (uint32_t)period_us;
                if (!burst_period_min || p < burst_period_min) burst_period_min = p;
                if (!burst_period_max || p > burst_period_max) burst_period_max = p;
                if (p < PERIOD_MIN_US || p > PERIOD_MAX_US) {
                    burst_period_bad++;
                }
            }
        }
    } else {
        begin_burst(rise_us, end_us, width_us);
    }

    last_valid_rise_us = rise_us;

    lock_state();
    if (active_run[0]) {
        run_servo_valid_pulses++;
    }
    unlock_state();

    return period_us;
}

static void process_high_pulse(int64_t rise_us, uint32_t width_us)
{
    int64_t end_us = rise_us + width_us;

    lock_state();
    pulse_seq++;
    uint32_t this_pulse = pulse_seq;
    unlock_state();

    if (width_us >= SERVO_MIN_US && width_us <= SERVO_MAX_US) {
        int64_t period_us = add_valid_pulse(rise_us, end_us, width_us);

        cJSON *obj = new_event("pulse");
        if (obj) {
            cJSON_AddNumberToObject(obj, "pulse_seq", this_pulse);
            cJSON_AddStringToObject(obj, "pulse_class", "servo_valid");
            cJSON_AddNumberToObject(obj, "rise_us", (double)rise_us);
            cJSON_AddNumberToObject(obj, "end_us", (double)end_us);
            cJSON_AddNumberToObject(obj, "width_us", width_us);
            if (period_us >= 0) cJSON_AddNumberToObject(obj, "period_us", (double)period_us);
            else cJSON_AddNullToObject(obj, "period_us");
            cJSON_AddNumberToObject(obj, "burst", burst_seq);
            write_event(obj);
        }
    } else {
        lock_state();
        if (active_run[0]) {
            run_transients++;
        }
        unlock_state();

        cJSON *obj = new_event("pulse");
        if (obj) {
            cJSON_AddNumberToObject(obj, "pulse_seq", this_pulse);
            cJSON_AddStringToObject(obj, "pulse_class", "transient");
            cJSON_AddNumberToObject(obj, "rise_us", (double)rise_us);
            cJSON_AddNumberToObject(obj, "end_us", (double)end_us);
            cJSON_AddNumberToObject(obj, "width_us", width_us);
            write_event(obj);
        }
    }
}

static void process_capture_block(const capture_block_t *block)
{
    uint64_t total_us = 0;
    for (size_t i = 0; i < block->num_symbols; ++i) {
        total_us += block->symbols[i].duration0;
        total_us += block->symbols[i].duration1;
    }

    int64_t start_est_us = block->done_us - RX_IDLE_STOP_US - (int64_t)total_us;
    uint64_t cursor_us = 0;

    for (size_t i = 0; i < block->num_symbols; ++i) {
        const rmt_symbol_word_t *s = &block->symbols[i];

        if (s->duration0) {
            if (s->level0) {
                process_high_pulse(start_est_us + (int64_t)cursor_us, s->duration0);
            }
            cursor_us += s->duration0;
        }

        if (s->duration1) {
            if (s->level1) {
                process_high_pulse(start_est_us + (int64_t)cursor_us, s->duration1);
            }
            cursor_us += s->duration1;
        }
    }

    lock_state();
    last_edge_us = start_est_us + (int64_t)cursor_us;
    unlock_state();
}

static bool IRAM_ATTR rmt_rx_done_cb(rmt_channel_handle_t channel,
                                      const rmt_rx_done_event_data_t *edata,
                                      void *user_data)
{
    (void)channel;
    QueueHandle_t q = (QueueHandle_t)user_data;
    BaseType_t high_task_wakeup = pdFALSE;
    xQueueOverwriteFromISR(q, edata, &high_task_wakeup);
    return high_task_wakeup == pdTRUE;
}

static void rmt_acquisition_task(void *arg)
{
    (void)arg;
    static rmt_symbol_word_t rx_buffer[RX_BUFFER_SYMBOLS];

    rmt_receive_config_t receive_cfg = {
        .signal_range_min_ns = RX_SIGNAL_MIN_NS,
        .signal_range_max_ns = RX_SIGNAL_MAX_NS,
    };

    while (true) {
        esp_err_t err = rmt_receive(rx_channel, rx_buffer, sizeof(rx_buffer), &receive_cfg);
        if (err != ESP_OK) {
            lock_state();
            capture_errors++;
            unlock_state();
            vTaskDelay(pdMS_TO_TICKS(50));
            continue;
        }

        rmt_rx_done_event_data_t evt;
        if (xQueueReceive(rmt_done_queue, &evt, portMAX_DELAY) != pdTRUE) {
            lock_state();
            capture_errors++;
            unlock_state();
            continue;
        }

        capture_block_t block;
        memset(&block, 0, sizeof(block));
        block.done_us = esp_timer_get_time();
        block.num_symbols = evt.num_symbols;

        if (block.num_symbols >= RX_BUFFER_SYMBOLS) {
            lock_state();
            capture_truncations++;
            unlock_state();
            if (block.num_symbols > RX_BUFFER_SYMBOLS) {
                block.num_symbols = RX_BUFFER_SYMBOLS;
            }
        }

        memcpy(block.symbols, evt.received_symbols,
               block.num_symbols * sizeof(rmt_symbol_word_t));

        if (xQueueSend(capture_queue, &block, 0) != pdTRUE) {
            lock_state();
            capture_overflows++;
            unlock_state();
        }
    }
}

static void capture_processing_task(void *arg)
{
    (void)arg;
    capture_block_t block;

    while (true) {
        if (xQueueReceive(capture_queue, &block, pdMS_TO_TICKS(20)) == pdTRUE) {
            process_capture_block(&block);
        } else if (burst_active) {
            int64_t now = esp_timer_get_time();
            if (now - burst_last_rise_us >= BURST_GAP_US) {
                close_burst("quiet_gap");
            }
        }
    }
}

static bool init_rmt_capture(void)
{
    rmt_done_queue = xQueueCreate(1, sizeof(rmt_rx_done_event_data_t));
    capture_queue = xQueueCreate(CAPTURE_QUEUE_DEPTH, sizeof(capture_block_t));
    if (!rmt_done_queue || !capture_queue) {
        return false;
    }

    rmt_rx_channel_config_t rx_cfg = {
        .gpio_num = WITNESS_GPIO,
        .clk_src = RMT_CLK_SRC_DEFAULT,
        .resolution_hz = RMT_RESOLUTION_HZ,
        .mem_block_symbols = 64,
        .flags = {
            .invert_in = false,
            .with_dma = false,
        },
    };

    esp_err_t err = rmt_new_rx_channel(&rx_cfg, &rx_channel);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "rmt_new_rx_channel: %s", esp_err_to_name(err));
        return false;
    }

    rmt_rx_event_callbacks_t cbs = {
        .on_recv_done = rmt_rx_done_cb,
    };
    err = rmt_rx_register_event_callbacks(rx_channel, &cbs, rmt_done_queue);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "rmt_rx_register_event_callbacks: %s", esp_err_to_name(err));
        return false;
    }
    err = rmt_enable(rx_channel);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "rmt_enable: %s", esp_err_to_name(err));
        return false;
    }

    if (xTaskCreatePinnedToCore(rmt_acquisition_task, "w007_rmt_acq", 4096, NULL, 12, NULL, 1) != pdPASS) {
        return false;
    }
    if (xTaskCreatePinnedToCore(capture_processing_task, "w007_capture_proc", 6144, NULL, 8, NULL, 1) != pdPASS) {
        return false;
    }

    return true;
}

static void wifi_event_handler(void *arg, esp_event_base_t event_base,
                               int32_t event_id, void *event_data)
{
    (void)arg;

    if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_DISCONNECTED) {
        wifi_connected = false;
        snprintf(current_ip, sizeof(current_ip), "0.0.0.0");
        return;
    }

    if (event_base == IP_EVENT && event_id == IP_EVENT_STA_GOT_IP) {
        ip_event_got_ip_t *event = (ip_event_got_ip_t *)event_data;
        snprintf(current_ip, sizeof(current_ip), IPSTR, IP2STR(&event->ip_info.ip));
        wifi_connected = true;
    }
}

static bool init_wifi(void)
{
    esp_err_t err = esp_netif_init();
    if (err != ESP_OK && err != ESP_ERR_INVALID_STATE) {
        ESP_LOGE(TAG, "esp_netif_init: %s", esp_err_to_name(err));
        return false;
    }

    err = esp_event_loop_create_default();
    if (err != ESP_OK && err != ESP_ERR_INVALID_STATE) {
        ESP_LOGE(TAG, "event loop: %s", esp_err_to_name(err));
        return false;
    }

    esp_netif_t *sta = esp_netif_create_default_wifi_sta();
    if (!sta) {
        return false;
    }
    esp_netif_set_hostname(sta, DEVICE_ID);

    wifi_init_config_t wifi_init_cfg = WIFI_INIT_CONFIG_DEFAULT();
    err = esp_wifi_init(&wifi_init_cfg);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "esp_wifi_init: %s", esp_err_to_name(err));
        return false;
    }

    esp_event_handler_register(WIFI_EVENT, ESP_EVENT_ANY_ID, &wifi_event_handler, NULL);
    esp_event_handler_register(IP_EVENT, IP_EVENT_STA_GOT_IP, &wifi_event_handler, NULL);

    esp_wifi_set_storage(WIFI_STORAGE_FLASH);
    esp_wifi_set_mode(WIFI_MODE_STA);

    wifi_config_t sta_cfg;
    memset(&sta_cfg, 0, sizeof(sta_cfg));
    err = esp_wifi_get_config(WIFI_IF_STA, &sta_cfg);
    if (err != ESP_OK) {
        memset(&sta_cfg, 0, sizeof(sta_cfg));
    }

    if (sta_cfg.sta.ssid[0] == '\0' && W007_WIFI_SSID[0] != '\0') {
        snprintf((char *)sta_cfg.sta.ssid, sizeof(sta_cfg.sta.ssid), "%s", W007_WIFI_SSID);
        snprintf((char *)sta_cfg.sta.password, sizeof(sta_cfg.sta.password), "%s", W007_WIFI_PASSWORD);
        sta_cfg.sta.bssid_set = 0;
        err = esp_wifi_set_config(WIFI_IF_STA, &sta_cfg);
        if (err != ESP_OK) {
            ESP_LOGE(TAG, "esp_wifi_set_config: %s", esp_err_to_name(err));
            memset(&sta_cfg, 0, sizeof(sta_cfg));
        }
    }

    if (sta_cfg.sta.ssid[0] != '\0') {
        wifi_configured = true;
        snprintf(configured_ssid, sizeof(configured_ssid), "%s", (char *)sta_cfg.sta.ssid);
    }

    err = esp_wifi_start();
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "esp_wifi_start: %s", esp_err_to_name(err));
        return false;
    }

    esp_wifi_set_ps(WIFI_PS_NONE);

    if (wifi_configured) {
        cJSON *obj = new_event("wifi_connect_begin");
        if (obj) {
            cJSON_AddStringToObject(obj, "ssid", configured_ssid);
            cJSON_AddStringToObject(obj, "credential_source",
                                    W007_WIFI_SSID[0] ? "stored_or_fallback" : "stored_nvs");
            write_event(obj);
        }
        esp_wifi_connect();
    } else {
        cJSON *obj = new_event("wifi_disabled");
        if (obj) {
            cJSON_AddStringToObject(obj, "reason", "station_config_unavailable");
            write_event(obj);
        }
    }

    return true;
}

static void add_reply_identity(cJSON *obj)
{
    lock_state();
    cJSON_AddStringToObject(obj, "device_id", DEVICE_ID);
    cJSON_AddStringToObject(obj, "session", session_id);
    cJSON_AddStringToObject(obj, "run", active_run[0] ? active_run : "NONE");
    unlock_state();
}

static void send_reply(int sock, const struct sockaddr_in *addr, cJSON *obj)
{
    if (!obj) return;
    add_reply_identity(obj);
    char *line = cJSON_PrintUnformatted(obj);
    if (line) {
        sendto(sock, line, strlen(line), 0, (const struct sockaddr *)addr, sizeof(*addr));
        free(line);
    }
    cJSON_Delete(obj);
}

static bool run_file_exists(const char *path)
{
    struct stat st;
    return stat(path, &st) == 0;
}

static void make_run_names(const char *run_id, char *base, size_t base_len,
                           char *path, size_t path_len)
{
    snprintf(base, base_len, "R_%s.jl", run_id);
    snprintf(path, path_len, "%s/%s", EVIDENCE_BASE, base);
}

static bool start_run(const char *new_run, const char *utc_anchor,
                      char *detail, size_t detail_len)
{
    if (!storage_ready) {
        snprintf(detail, detail_len, "evidence_storage_unavailable");
        return false;
    }
    if (!rmt_ready) {
        snprintf(detail, detail_len, "capture_unavailable");
        return false;
    }
    if (!valid_run_name(new_run)) {
        snprintf(detail, detail_len, "invalid_run_id");
        return false;
    }

    lock_state();
    if (active_run[0]) {
        unlock_state();
        snprintf(detail, detail_len, "run_already_active");
        return false;
    }
    int64_t edge = last_edge_us;
    unlock_state();

    int64_t now = esp_timer_get_time();
    if (edge > 0 && now - edge < RUN_START_QUIET_US) {
        snprintf(detail, detail_len, "witness_not_quiet");
        return false;
    }
    if (uxQueueMessagesWaiting(capture_queue) != 0 || burst_active) {
        snprintf(detail, detail_len, "capture_not_drained");
        return false;
    }

    char base[RUN_NAME_MAX];
    char path[RUN_NAME_MAX];
    make_run_names(new_run, base, sizeof(base), path, sizeof(path));
    if (run_file_exists(path)) {
        snprintf(detail, detail_len, "run_file_already_exists");
        return false;
    }

    FILE *f = fopen(path, "a");
    if (!f) {
        snprintf(detail, detail_len, "run_file_open_failed");
        return false;
    }

    lock_state();
    run_file = f;
    snprintf(active_run, sizeof(active_run), "%s", new_run);
    snprintf(active_run_anchor, sizeof(active_run_anchor), "%s", utc_anchor ? utc_anchor : "");
    snprintf(active_run_basename, sizeof(active_run_basename), "%s", base);
    snprintf(active_run_path, sizeof(active_run_path), "%s", path);
    run_start_us = now;
    run_servo_valid_pulses = 0;
    run_transients = 0;
    run_bursts = 0;
    run_servo_like_bursts = 0;
    run_capture_overflows_start = capture_overflows;
    run_capture_truncations_start = capture_truncations;
    run_capture_errors_start = capture_errors;
    last_valid_rise_us = 0;
    unlock_state();

    cJSON *obj = new_event("run_start");
    if (obj) {
        cJSON_AddNumberToObject(obj, "run_start_us", (double)now);
        if (utc_anchor && utc_anchor[0]) cJSON_AddStringToObject(obj, "coordinator_utc", utc_anchor);
        else cJSON_AddNullToObject(obj, "coordinator_utc");
        cJSON_AddStringToObject(obj, "evidence_file", base);
        cJSON_AddNumberToObject(obj, "gpio", WITNESS_GPIO);
        cJSON_AddStringToObject(obj, "capture_engine", "rmt_rx");
        write_event(obj);
    }

    lock_state();
    sync_file(run_file);
    sync_file(session_file);
    unlock_state();

    snprintf(detail, detail_len, "%s", base);
    return true;
}

static bool stop_run(const char *utc_anchor, char *detail, size_t detail_len)
{
    lock_state();
    bool active = active_run[0] != '\0';
    unlock_state();
    if (!active) {
        snprintf(detail, detail_len, "no_active_run");
        return false;
    }

    int64_t deadline = esp_timer_get_time() + (STOP_QUIET_TIMEOUT_MS * 1000LL);
    while (esp_timer_get_time() < deadline) {
        lock_state();
        int64_t edge = last_edge_us;
        unlock_state();
        int64_t now = esp_timer_get_time();
        bool quiet = (edge == 0 || now - edge >= BURST_GAP_US);
        if (quiet && uxQueueMessagesWaiting(capture_queue) == 0 && !burst_active) {
            break;
        }
        vTaskDelay(pdMS_TO_TICKS(20));
    }

    if (burst_active) {
        snprintf(detail, detail_len, "capture_not_quiet");
        return false;
    }

    int64_t stop_us = esp_timer_get_time();

    char completed_run[MAX_RUN_ID_LEN + 1];
    char completed_base[RUN_NAME_MAX];
    char completed_path[RUN_NAME_MAX];
    char start_anchor[64];
    uint32_t servo_pulses, transients, bursts, servo_bursts;
    uint32_t run_overflows, run_truncations, run_errors;
    int64_t start_us;
    int64_t edge;

    lock_state();
    snprintf(completed_run, sizeof(completed_run), "%s", active_run);
    snprintf(completed_base, sizeof(completed_base), "%s", active_run_basename);
    snprintf(completed_path, sizeof(completed_path), "%s", active_run_path);
    snprintf(start_anchor, sizeof(start_anchor), "%s", active_run_anchor);
    start_us = run_start_us;
    servo_pulses = run_servo_valid_pulses;
    transients = run_transients;
    bursts = run_bursts;
    servo_bursts = run_servo_like_bursts;
    run_overflows = capture_overflows - run_capture_overflows_start;
    run_truncations = capture_truncations - run_capture_truncations_start;
    run_errors = capture_errors - run_capture_errors_start;
    edge = last_edge_us;
    unlock_state();

    cJSON *obj = new_event("run_end");
    if (obj) {
        cJSON_AddStringToObject(obj, "reason", "operator");
        cJSON_AddNumberToObject(obj, "run_start_us", (double)start_us);
        cJSON_AddNumberToObject(obj, "run_end_us", (double)stop_us);
        cJSON_AddNumberToObject(obj, "duration_us", (double)(stop_us - start_us));
        if (start_anchor[0]) cJSON_AddStringToObject(obj, "start_coordinator_utc", start_anchor);
        else cJSON_AddNullToObject(obj, "start_coordinator_utc");
        if (utc_anchor && utc_anchor[0]) cJSON_AddStringToObject(obj, "stop_coordinator_utc", utc_anchor);
        else cJSON_AddNullToObject(obj, "stop_coordinator_utc");
        cJSON_AddNumberToObject(obj, "servo_valid_pulses", servo_pulses);
        cJSON_AddNumberToObject(obj, "transients", transients);
        cJSON_AddNumberToObject(obj, "bursts", bursts);
        cJSON_AddNumberToObject(obj, "servo_like_bursts", servo_bursts);
        if (edge > 0) cJSON_AddNumberToObject(obj, "quiet_before_stop_us", (double)(stop_us - edge));
        else cJSON_AddNullToObject(obj, "quiet_before_stop_us");
        cJSON_AddNumberToObject(obj, "capture_overflows_during_run", run_overflows);
        cJSON_AddNumberToObject(obj, "capture_truncations_during_run", run_truncations);
        cJSON_AddNumberToObject(obj, "capture_errors_during_run", run_errors);
        write_event(obj);
    }

    lock_state();
    sync_file(run_file);
    if (run_file) {
        fclose(run_file);
        run_file = NULL;
    }
    active_run[0] = '\0';
    active_run_anchor[0] = '\0';
    active_run_basename[0] = '\0';
    active_run_path[0] = '\0';
    run_start_us = 0;
    last_valid_rise_us = 0;
    sync_file(session_file);
    unlock_state();

    char digest[65];
    if (!sha256_file(completed_path, digest)) {
        snprintf(detail, detail_len, "run_hash_failed");
        return false;
    }

    char sidecar[RUN_NAME_MAX + 16];
    snprintf(sidecar, sizeof(sidecar), "%s.sha", completed_path);
    FILE *sf = fopen(sidecar, "w");
    if (!sf) {
        snprintf(detail, detail_len, "sidecar_open_failed");
        return false;
    }
    fprintf(sf, "%s  %s\n", digest, completed_base);
    sync_file(sf);
    fclose(sf);

    cJSON *closed = new_event("run_file_closed");
    if (closed) {
        cJSON_AddStringToObject(closed, "completed_run", completed_run);
        cJSON_AddStringToObject(closed, "evidence_file", completed_base);
        cJSON_AddStringToObject(closed, "sha256", digest);
        char sidecar_base[RUN_NAME_MAX + 16];
        snprintf(sidecar_base, sizeof(sidecar_base), "%s.sha", completed_base);
        cJSON_AddStringToObject(closed, "sidecar", sidecar_base);
        write_event(closed);
    }

    snprintf(detail, detail_len, "%s", digest);
    return true;
}

static void send_status_reply(int sock, const struct sockaddr_in *addr, bool discover)
{
    cJSON *obj = new_event(discover ? "discover_reply" : "status_reply");
    if (!obj) return;

    lock_state();
    bool connected = wifi_connected;
    char ip[IP_STRING_MAX];
    snprintf(ip, sizeof(ip), "%s", current_ip);
    uint32_t ps = pulse_seq;
    uint32_t bs = burst_seq;
    uint32_t ov = capture_overflows;
    uint32_t tr = capture_truncations;
    uint32_t er = capture_errors;
    unlock_state();

    cJSON_AddStringToObject(obj, "ip", ip);
    cJSON_AddBoolToObject(obj, "connected", connected);
    cJSON_AddNumberToObject(obj, "control_port", CONTROL_PORT);
    cJSON_AddNumberToObject(obj, "gpio", WITNESS_GPIO);
    cJSON_AddStringToObject(obj, "capture_engine", "rmt_rx");
    cJSON_AddBoolToObject(obj, "capture_ready", rmt_ready);
    cJSON_AddNumberToObject(obj, "capture_queue_depth", uxQueueMessagesWaiting(capture_queue));
    cJSON_AddNumberToObject(obj, "capture_overflows", ov);
    cJSON_AddNumberToObject(obj, "capture_truncations", tr);
    cJSON_AddNumberToObject(obj, "capture_errors", er);
    cJSON_AddNumberToObject(obj, "rx_buffer_symbols", RX_BUFFER_SYMBOLS);
    cJSON_AddNumberToObject(obj, "capture_filter_min_ns", RX_SIGNAL_MIN_NS);
    cJSON_AddNumberToObject(obj, "pulse_seq", ps);
    cJSON_AddNumberToObject(obj, "burst_seq", bs);
    cJSON_AddStringToObject(obj, "session_file", session_basename);

    send_reply(sock, addr, obj);
}

static bool run_selftest_pwm(char *detail, size_t detail_len)
{
    lock_state();
    bool active = active_run[0] != '\0';
    unlock_state();

    if (!active) {
        snprintf(detail, detail_len, "selftest_requires_active_run");
        return false;
    }

    gpio_config_t io = {
        .pin_bit_mask = (1ULL << SELFTEST_GPIO),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };

    esp_err_t err = gpio_config(&io);
    if (err != ESP_OK) {
        snprintf(detail, detail_len, "gpio_config:%s", esp_err_to_name(err));
        return false;
    }

    gpio_set_level(SELFTEST_GPIO, 0);
    vTaskDelay(pdMS_TO_TICKS(100));

    for (int i = 0; i < 50; ++i) {
        gpio_set_level(SELFTEST_GPIO, 1);
        esp_rom_delay_us(2000);
        gpio_set_level(SELFTEST_GPIO, 0);
        vTaskDelay(pdMS_TO_TICKS(18));
    }

    gpio_set_level(SELFTEST_GPIO, 0);

    snprintf(detail, detail_len, "50_pulses_2000us_high_approx_20ms_period");
    return true;
}
static void handle_udp_command(int sock, char *text, const struct sockaddr_in *addr)
{
    while (*text == ' ') text++;
    size_t n = strlen(text);
    while (n && (text[n - 1] == '\r' || text[n - 1] == '\n' || text[n - 1] == ' ')) {
        text[--n] = '\0';
    }

    char *save = NULL;
    char *magic = strtok_r(text, " ", &save);
    char *command = strtok_r(NULL, " ", &save);
    if (!magic || !command || strcmp(magic, CONTROL_MAGIC) != 0) {
        return;
    }

    if (strcasecmp(command, "DISCOVER") == 0) {
        send_status_reply(sock, addr, true);
        return;
    }
    if (strcasecmp(command, "STATUS") == 0) {
        send_status_reply(sock, addr, false);
        return;
    }
    if (strcasecmp(command, "START") == 0) {
        char *run = strtok_r(NULL, " ", &save);
        char *utc = strtok_r(NULL, " ", &save);
        char detail[RUN_NAME_MAX];
        bool ok = run && start_run(run, utc, detail, sizeof(detail));
        if (!run) snprintf(detail, sizeof(detail), "START_requires_run_id");
        cJSON *obj = new_event("start_reply");
        if (obj) {
            cJSON_AddBoolToObject(obj, "ok", ok);
            cJSON_AddStringToObject(obj, "detail", detail);
            send_reply(sock, addr, obj);
        }
        return;
    }
    if (strcasecmp(command, "MARK") == 0) {
        const char *mark = save ? save : "";
        while (*mark == ' ') mark++;
        cJSON *ev = new_event("mark");
        if (ev) {
            cJSON_AddStringToObject(ev, "text", mark);
            char src[IP_STRING_MAX];
            inet_ntop(AF_INET, &addr->sin_addr, src, sizeof(src));
            cJSON_AddStringToObject(ev, "source_ip", src);
            write_event(ev);
        }
        cJSON *obj = new_event("mark_reply");
        if (obj) {
            cJSON_AddBoolToObject(obj, "ok", true);
            cJSON_AddStringToObject(obj, "text", mark);
            send_reply(sock, addr, obj);
        }
        return;
    }
    if (strcasecmp(command, "SELFTEST") == 0) {
        char detail[128];
        bool ok = run_selftest_pwm(detail, sizeof(detail));
        cJSON *obj = new_event("selftest_reply");
        if (obj) {
            cJSON_AddBoolToObject(obj, "ok", ok);
            cJSON_AddStringToObject(obj, "detail", detail);
            send_reply(sock, addr, obj);
        }
        return;
    }
    if (strcasecmp(command, "STOP") == 0) {
        char *utc = strtok_r(NULL, " ", &save);
        char detail[RUN_NAME_MAX];
        bool ok = stop_run(utc, detail, sizeof(detail));
        cJSON *obj = new_event("stop_reply");
        if (obj) {
            cJSON_AddBoolToObject(obj, "ok", ok);
            cJSON_AddStringToObject(obj, "detail", detail);
            send_reply(sock, addr, obj);
        }
        return;
    }

    cJSON *obj = new_event("command_error");
    if (obj) {
        cJSON_AddStringToObject(obj, "reason", "unknown_command");
        cJSON_AddStringToObject(obj, "command", command);
        send_reply(sock, addr, obj);
    }
}

static void udp_control_task(void *arg)
{
    (void)arg;

    int sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_IP);
    if (sock < 0) {
        ESP_LOGE(TAG, "socket failed: errno=%d", errno);
        vTaskDelete(NULL);
        return;
    }

    int yes = 1;
    setsockopt(sock, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof(yes));
    struct timeval tv = {.tv_sec = 0, .tv_usec = 200000};
    setsockopt(sock, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));

    struct sockaddr_in bind_addr = {
        .sin_family = AF_INET,
        .sin_port = htons(CONTROL_PORT),
        .sin_addr.s_addr = htonl(INADDR_ANY),
    };

    if (bind(sock, (struct sockaddr *)&bind_addr, sizeof(bind_addr)) != 0) {
        ESP_LOGE(TAG, "bind failed: errno=%d", errno);
        close(sock);
        vTaskDelete(NULL);
        return;
    }

    udp_ready = true;
    cJSON *ready = new_event("control_ready");
    if (ready) {
        cJSON_AddStringToObject(ready, "transport", "udp");
        cJSON_AddNumberToObject(ready, "port", CONTROL_PORT);
        write_event(ready);
    }

    char buf[512];
    while (true) {
        struct sockaddr_in source;
        socklen_t slen = sizeof(source);
        int len = recvfrom(sock, buf, sizeof(buf) - 1, 0,
                           (struct sockaddr *)&source, &slen);
        if (len < 0) {
            if (errno == EAGAIN || errno == EWOULDBLOCK) {
                continue;
            }
            vTaskDelay(pdMS_TO_TICKS(100));
            continue;
        }
        buf[len] = '\0';
        handle_udp_command(sock, buf, &source);
    }
}

static void housekeeping_task(void *arg)
{
    (void)arg;
    int64_t last_heartbeat_us = esp_timer_get_time();
    int64_t last_reconnect_us = 0;

    while (true) {
        int64_t now = esp_timer_get_time();

        bool connected = wifi_connected;
        if (connected != last_reported_wifi) {
            cJSON *obj = new_event(connected ? "wifi_connected" : "wifi_disconnected");
            if (obj) {
                cJSON_AddStringToObject(obj, "ip", current_ip);
                if (connected) cJSON_AddStringToObject(obj, "ssid", configured_ssid);
                write_event(obj);
            }
            last_reported_wifi = connected;
        }

        lock_state();
        uint32_t ov = capture_overflows;
        uint32_t tr = capture_truncations;
        uint32_t er = capture_errors;
        bool run_active = active_run[0] != '\0';
        unlock_state();

        if (ov != last_reported_overflows || tr != last_reported_truncations || er != last_reported_errors) {
            cJSON *obj = new_event("capture_health_change");
            if (obj) {
                cJSON_AddNumberToObject(obj, "capture_overflows", ov);
                cJSON_AddNumberToObject(obj, "capture_truncations", tr);
                cJSON_AddNumberToObject(obj, "capture_errors", er);
                write_event(obj);
            }
            last_reported_overflows = ov;
            last_reported_truncations = tr;
            last_reported_errors = er;
        }

        if (now - last_heartbeat_us >= 5000000LL) {
            cJSON *obj = new_event("heartbeat");
            if (obj) {
                cJSON_AddBoolToObject(obj, "wifi_connected", wifi_connected);
                cJSON_AddStringToObject(obj, "ip", current_ip);
                cJSON_AddNumberToObject(obj, "capture_queue_depth", uxQueueMessagesWaiting(capture_queue));
                cJSON_AddNumberToObject(obj, "capture_overflows", ov);
                cJSON_AddNumberToObject(obj, "capture_truncations", tr);
                cJSON_AddNumberToObject(obj, "capture_errors", er);
                cJSON_AddStringToObject(obj, "active_run", run_active ? active_run : "NONE");
                write_event(obj);
            }
            last_heartbeat_us = now;
        }

        if (!run_active && wifi_configured && !wifi_connected && now - last_reconnect_us >= 5000000LL) {
            esp_wifi_connect();
            last_reconnect_us = now;
        }

        vTaskDelay(pdMS_TO_TICKS(100));
    }
}

void app_main(void)
{
    setvbuf(stdout, NULL, _IONBF, 0);
    printf("\nW007_RMT_WITNESS_BOOT\n");

    state_mutex = xSemaphoreCreateMutex();
    if (!state_mutex) {
        printf("W007_FATAL state_mutex\n");
        return;
    }

    psa_status_t psa_status = psa_crypto_init();
    if (psa_status != PSA_SUCCESS) {
        printf("W007_FATAL_PSA_INIT status=%ld\n", (long)psa_status);
        return;
    }

    esp_err_t nvs_err = nvs_flash_init();
    bool nvs_ok = (nvs_err == ESP_OK);
    if (!nvs_ok) {
        printf("W007_NVS_INIT_FAIL %s\n", esp_err_to_name(nvs_err));
    }

    uint8_t mac[6] = {0};
    esp_read_mac(mac, ESP_MAC_WIFI_STA);
    snprintf(uid_short, sizeof(uid_short), "%02x%02x%02x%02x",
             mac[2], mac[3], mac[4], mac[5]);

    boot_counter = next_boot_counter(nvs_ok);
    snprintf(session_id, sizeof(session_id), "%s-%s-B%04" PRIu32,
             DEVICE_ID, uid_short, boot_counter);
    snprintf(session_basename, sizeof(session_basename), "S_%s_B%04" PRIu32 ".jl", uid_short, boot_counter);
    snprintf(session_path, sizeof(session_path), "%s/%s", EVIDENCE_BASE, session_basename);

    storage_ready = mount_evidence_storage();
    if (!storage_ready) {
        printf("W007_FATAL_EVIDENCE_STORAGE\n");
        while (true) vTaskDelay(pdMS_TO_TICKS(1000));
    }

    session_file = fopen(session_path, "a");
    if (!session_file) {
        printf("W007_FATAL_SESSION_FILE errno=%d\n", errno);
        while (true) vTaskDelay(pdMS_TO_TICKS(1000));
    }

    cJSON *session = new_event("session_start");
    if (session) {
        cJSON_AddNumberToObject(session, "gpio", WITNESS_GPIO);
        cJSON_AddStringToObject(session, "authority_role", "NONE");
        cJSON_AddStringToObject(session, "authorization_role", "NONE");
        cJSON_AddStringToObject(session, "capture_engine", "rmt_rx");
        cJSON_AddNumberToObject(session, "rmt_resolution_hz", RMT_RESOLUTION_HZ);
        cJSON_AddNumberToObject(session, "capture_filter_min_ns", RX_SIGNAL_MIN_NS);
        cJSON_AddNumberToObject(session, "capture_idle_stop_us", RX_IDLE_STOP_US);
        cJSON_AddNumberToObject(session, "rx_buffer_symbols", RX_BUFFER_SYMBOLS);
        cJSON_AddBoolToObject(session, "absolute_edge_time_estimated", true);
        cJSON_AddStringToObject(session, "edge_time_basis", "rx_done_minus_idle_stop_minus_captured_durations");
        cJSON_AddBoolToObject(session, "capture_health_required_zero", true);
        cJSON_AddNumberToObject(session, "servo_min_us", SERVO_MIN_US);
        cJSON_AddNumberToObject(session, "servo_max_us", SERVO_MAX_US);
        cJSON_AddNumberToObject(session, "period_min_us", PERIOD_MIN_US);
        cJSON_AddNumberToObject(session, "period_max_us", PERIOD_MAX_US);
        cJSON_AddNumberToObject(session, "burst_gap_us", BURST_GAP_US);
        cJSON_AddNumberToObject(session, "run_start_quiet_us", RUN_START_QUIET_US);
        cJSON_AddStringToObject(session, "session_file", session_basename);
        write_event(session);
    }

    rmt_ready = init_rmt_capture();
    if (!rmt_ready) {
        cJSON *obj = new_event("capture_start_failed");
        if (obj) write_event(obj);
        printf("W007_FATAL_RMT_CAPTURE\n");
        while (true) vTaskDelay(pdMS_TO_TICKS(1000));
    }

    if (nvs_ok) {
        init_wifi();
    } else {
        cJSON *obj = new_event("wifi_disabled");
        if (obj) {
            cJSON_AddStringToObject(obj, "reason", "nvs_unavailable");
            write_event(obj);
        }
    }

    xTaskCreatePinnedToCore(udp_control_task, "w007_udp", 6144, NULL, 6, NULL, 0);
    xTaskCreatePinnedToCore(housekeeping_task, "w007_house", 6144, NULL, 4, NULL, 0);

    vTaskDelay(pdMS_TO_TICKS(100));

    cJSON *ready = new_event("witness_ready");
    if (ready) {
        cJSON_AddNumberToObject(ready, "gpio", WITNESS_GPIO);
        cJSON_AddStringToObject(ready, "capture_engine", "rmt_rx");
        cJSON_AddBoolToObject(ready, "capture_ready", rmt_ready);
        cJSON_AddBoolToObject(ready, "network_control", udp_ready);
        cJSON_AddNumberToObject(ready, "capture_overflows", capture_overflows);
        cJSON_AddNumberToObject(ready, "capture_truncations", capture_truncations);
        cJSON_AddNumberToObject(ready, "capture_errors", capture_errors);
        write_event(ready);
    }

    while (true) {
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}






