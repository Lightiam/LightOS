/* SPDX-License-Identifier: GPL-2.0 */
#ifndef _LIGHTOS_PHOTONIC_DRIVER_H
#define _LIGHTOS_PHOTONIC_DRIVER_H

#include <linux/types.h>
#include <linux/device.h>
#include <linux/interrupt.h>
#include <linux/workqueue.h>

/*
 * LightOS Photonic NPU Driver
 *
 * Low-level driver for optical neural network accelerators.
 * Includes precision analog signal control and thermal management.
 */

#define PHOTONIC_MAX_DEVICES 16
#define PHOTONIC_MAX_MZI 1024          /* Mach-Zehnder Interferometers */
#define PHOTONIC_MAX_WAVELENGTHS 64    /* WDM channels */
#define PHOTONIC_MAX_POWER_RAILS 8

/* Device capabilities */
#define PHOTONIC_CAP_MZI         (1 << 0)  /* MZI-based computation */
#define PHOTONIC_CAP_MICRORING   (1 << 1)  /* Microring resonators */
#define PHOTONIC_CAP_COHERENT    (1 << 2)  /* Coherent detection */
#define PHOTONIC_CAP_WDM         (1 << 3)  /* Wavelength-division multiplexing */
#define PHOTONIC_CAP_THERMAL_CTRL (1 << 4) /* Active thermal control */

/* Thermal thresholds (millidegrees Celsius) */
#define THERMAL_TEMP_AMBIENT_MC      25000    /* 25°C */
#define THERMAL_TEMP_OPTIMAL_MC      45000    /* 45°C */
#define THERMAL_TEMP_WARNING_MC      75000    /* 75°C */
#define THERMAL_TEMP_CRITICAL_MC     85000    /* 85°C */
#define THERMAL_TEMP_EMERGENCY_MC    95000    /* 95°C */

/* Wavelength stability requirements */
#define WAVELENGTH_STABILITY_NM_PER_C  0.1f   /* 0.1nm/°C typical */

/* Power rail states */
enum power_rail_state {
    POWER_RAIL_OFF = 0,
    POWER_RAIL_RAMPING_UP = 1,
    POWER_RAIL_ON = 2,
    POWER_RAIL_RAMPING_DOWN = 3,
    POWER_RAIL_FAULT = 4,
};

/* Power rail configuration */
struct power_rail {
    __u8 rail_id;
    char name[32];                  /* e.g., "LASER_3.3V", "DAC_1.8V" */
    enum power_rail_state state;
    __u32 voltage_mv;               /* Voltage in millivolts */
    __u32 current_ma;               /* Current in milliamps */
    __u32 max_current_ma;           /* Maximum current */
    __u32 ramp_time_us;             /* Ramp-up/down time */
    bool overcurrent_fault;
    bool overvoltage_fault;
};

/* Thermal state */
struct thermal_state {
    __u32 temperature_mc;           /* Current temperature (millidegrees C) */
    __u32 threshold_warning_mc;
    __u32 threshold_critical_mc;
    __u32 threshold_emergency_mc;

    /* Thermal control */
    bool thermal_throttling_active;
    __u32 throttle_percent;         /* 0-100% */
    __u32 laser_power_percent;      /* Current laser power 0-100% */
    __u32 laser_power_max_percent;  /* Maximum allowed laser power */

    /* Cooling system */
    struct {
        __u32 fan_rpm;              /* Fan speed if present */
        __u32 fan_rpm_target;
        __u32 tec_current_ma;       /* Thermoelectric cooler current */
        __u32 tec_voltage_mv;
        bool tec_enabled;
        bool fan_enabled;
    } cooling;

    /* Temperature sensors */
    __u32 chip_temperature_mc;
    __u32 laser_temperature_mc;
    __u32 detector_temperature_mc;

    /* Statistics */
    __u64 thermal_events;
    __u64 throttling_events;
    __u64 emergency_shutdowns;
};

/* Mach-Zehnder Interferometer (MZI) configuration */
struct mzi_config {
    __u32 mzi_id;
    __u32 phase_shift_mdeg;         /* Phase shift in millidegrees (0-360000) */
    __u16 dac_value;                /* DAC code (typically 12-16 bit) */
    __u8 wavelength_channel;        /* WDM channel */
    bool enabled;
    float transmission;             /* Measured transmission (0.0-1.0) */
    float insertion_loss_db;        /* Insertion loss in dB */
};

/* Photodetector configuration */
struct photodetector_config {
    __u32 detector_id;
    __u16 adc_value;                /* ADC reading (typically 12-16 bit) */
    float optical_power_mw;         /* Optical power in milliwatts */
    __u32 responsivity_ma_per_mw;   /* Responsivity (mA/mW) */
    __u32 dark_current_na;          /* Dark current in nanoamps */
    bool saturated;
};

/* Photonic device info */
struct photonic_device_info {
    __u32 device_id;
    char device_name[64];
    __u32 capabilities;             /* Capability flags */

    /* Hardware specs */
    __u32 num_mzi;
    __u32 num_photodetectors;
    __u32 num_wavelengths;
    __u32 dac_resolution_bits;      /* Typically 12-16 */
    __u32 adc_resolution_bits;      /* Typically 12-16 */
    __u32 max_sample_rate_msps;     /* Mega-samples per second */

    /* Wavelength info */
    float center_wavelength_nm;     /* e.g., 1550nm for C-band */
    float wavelength_spacing_nm;    /* WDM channel spacing */

    /* Performance metrics */
    __u64 total_operations;
    __u64 total_matrix_ops;         /* Matrix-vector multiplications */
    float throughput_gops;          /* Giga-ops per second */
    float energy_efficiency_tops_per_w; /* Tera-ops per Watt */
};

/* Photonic operation types */
enum photonic_op_type {
    PHOTONIC_OP_MATRIX_VECTOR = 0,  /* Matrix-vector multiply */
    PHOTONIC_OP_CONVOLUTION = 1,    /* Convolution */
    PHOTONIC_OP_FFT = 2,            /* Fast Fourier Transform */
    PHOTONIC_OP_CUSTOM = 3,         /* Custom operation */
};

/* Photonic operation descriptor */
struct photonic_operation {
    enum photonic_op_type op_type;
    __u32 input_dim;
    __u32 output_dim;
    void *input_buffer;             /* Input data buffer */
    void *output_buffer;            /* Output data buffer */
    void *weight_matrix;            /* Weight matrix for MVM */
    __u32 wavelength_mask;          /* Which wavelengths to use (bitmap) */
    bool use_coherent_detection;    /* Use coherent vs. direct detection */
};

/* Device state */
enum photonic_device_state {
    PHOTONIC_STATE_UNINITIALIZED = 0,
    PHOTONIC_STATE_INITIALIZING = 1,
    PHOTONIC_STATE_READY = 2,
    PHOTONIC_STATE_BUSY = 3,
    PHOTONIC_STATE_THERMAL_LIMIT = 4,
    PHOTONIC_STATE_ERROR = 5,
    PHOTONIC_STATE_SHUTDOWN = 6,
};

/* Photonic device structure */
struct photonic_device {
    struct device *dev;
    void __iomem *mmio_base;        /* Memory-mapped I/O base */
    resource_size_t mmio_size;

    struct photonic_device_info info;
    enum photonic_device_state state;

    /* Power management */
    struct power_rail power_rails[PHOTONIC_MAX_POWER_RAILS];
    __u32 num_power_rails;
    bool power_good;

    /* Thermal management */
    struct thermal_state thermal;
    struct delayed_work thermal_work;
    struct workqueue_struct *thermal_wq;

    /* MZI array */
    struct mzi_config *mzi_array;
    spinlock_t mzi_lock;

    /* Photodetectors */
    struct photodetector_config *detectors;
    spinlock_t detector_lock;

    /* Interrupts */
    int irq;
    irqreturn_t (*irq_handler)(int, void *);

    /* Statistics */
    __u64 operations_completed;
    __u64 operations_failed;
    __u64 thermal_throttle_ns;      /* Total time spent throttled */
    ktime_t last_op_time;
};

/* Driver context */
struct photonic_driver_ctx {
    struct photonic_device *devices[PHOTONIC_MAX_DEVICES];
    __u32 num_devices;
    spinlock_t device_lock;
};

/* Function prototypes */

/* Device management */
int photonic_device_probe(struct device *dev);
void photonic_device_remove(struct device *dev);
int photonic_device_init(struct photonic_device *pdev);
void photonic_device_shutdown(struct photonic_device *pdev);

/* Power management */
int photonic_power_on(struct photonic_device *pdev);
int photonic_power_off(struct photonic_device *pdev);
int photonic_power_rail_control(struct photonic_device *pdev,
                               __u8 rail_id, bool enable);
void photonic_power_sequence(struct photonic_device *pdev);

/* Thermal management */
void photonic_thermal_monitor(struct work_struct *work);
int photonic_thermal_init(struct photonic_device *pdev);
void photonic_thermal_cleanup(struct photonic_device *pdev);
int photonic_thermal_set_threshold(struct photonic_device *pdev,
                                  __u32 warning_mc, __u32 critical_mc);
void photonic_thermal_emergency_shutdown(struct photonic_device *pdev);
int photonic_thermal_throttle(struct photonic_device *pdev, __u32 percent);

/* Cooling control */
int photonic_cooling_set_fan_speed(struct photonic_device *pdev, __u32 rpm);
int photonic_cooling_set_tec(struct photonic_device *pdev, bool enable,
                            __u32 current_ma);

/* MZI control */
int photonic_mzi_configure(struct photonic_device *pdev, __u32 mzi_id,
                          struct mzi_config *config);
int photonic_mzi_set_phase(struct photonic_device *pdev, __u32 mzi_id,
                           __u32 phase_mdeg);
int photonic_mzi_calibrate(struct photonic_device *pdev);

/* Photodetector */
int photonic_detector_read(struct photonic_device *pdev, __u32 detector_id,
                          struct photodetector_config *config);
float photonic_detector_get_power(struct photonic_device *pdev,
                                 __u32 detector_id);

/* Operations */
int photonic_execute_operation(struct photonic_device *pdev,
                              struct photonic_operation *op);
int photonic_matrix_vector_multiply(struct photonic_device *pdev,
                                   const float *matrix, const float *vector,
                                   float *result, __u32 rows, __u32 cols);

/* Calibration */
int photonic_calibrate_wavelengths(struct photonic_device *pdev);
int photonic_calibrate_power_levels(struct photonic_device *pdev);
int photonic_temperature_compensation(struct photonic_device *pdev);

/* Utility functions */
static inline bool photonic_is_thermal_safe(struct photonic_device *pdev)
{
    return pdev->thermal.temperature_mc < pdev->thermal.threshold_critical_mc;
}

static inline bool photonic_needs_throttle(struct photonic_device *pdev)
{
    return pdev->thermal.temperature_mc >= pdev->thermal.threshold_warning_mc;
}

static inline __u32 photonic_calculate_throttle_percent(struct photonic_device *pdev)
{
    if (pdev->thermal.temperature_mc < pdev->thermal.threshold_warning_mc)
        return 0;

    __u32 temp_above_warning = pdev->thermal.temperature_mc -
                               pdev->thermal.threshold_warning_mc;
    __u32 warning_to_critical = pdev->thermal.threshold_critical_mc -
                                pdev->thermal.threshold_warning_mc;

    if (warning_to_critical == 0)
        return 100;

    return min((__u32)100, (temp_above_warning * 100) / warning_to_critical);
}

#endif /* _LIGHTOS_PHOTONIC_DRIVER_H */
