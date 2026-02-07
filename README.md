# 💧 Syr Oceanic i-Lex Connect Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

Home Assistant integration for Syr Oceanic water softeners via the i-Lex Connect cloud service.

## ✨ Features

- 📊 **Real-time Monitoring**: Track water pressure, flow rate, and consumption
- 📈 **Water Usage Statistics**: Daily, weekly, monthly, and total water consumption
- 🔔 **Device Status**: Monitor regeneration cycles, alarms, and connectivity
- ⚡ **Energy Dashboard Integration**: Track water consumption in the Home Assistant energy dashboard
- 🔄 **Automatic Session Management**: Handles authentication and session renewal automatically

## 🔧 Supported Devices

- 💧 Syr Oceanic water softeners with i-Lex Connect module (L20, L10, etc.)

## 📦 Installation

### HACS (Recommended) ⭐

1. Open HACS in Home Assistant
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL and select "Integration" as the category
6. Click "Download" on the Syr Oceanic i-Lex Connect integration
7. Restart Home Assistant
8. Go to Settings → Devices & Services → Add Integration
9. Search for "Syr Oceanic i-Lex Connect"

### Manual Installation 🔨

1. Copy the `syr_oceanic_ilex_connect` folder to your `custom_components` directory
2. Restart Home Assistant
3. Go to Settings → Devices & Services → Add Integration
4. Search for "Syr Oceanic i-Lex Connect"

## ⚙️ Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for **Syr Oceanic i-Lex Connect**
4. Enter your i-Lex Connect credentials:
   - **Username**: Your i-Lex Connect account username
   - **Password**: Your i-Lex Connect account password
5. Click **Submit**

The integration will automatically discover all devices linked to your account.

## 📋 Entities

### 📊 Sensors

#### 💧 Water Consumption
- **Current Flow**: Real-time water flow rate (L)
- **Water Used Today**: Today's water consumption (m³)
- **Water Used Yesterday**: Yesterday's water consumption (m³)
- **Water Used This Week**: Current week's water consumption (m³)
- **Water Used Last Week**: Previous week's water consumption (m³)
- **Water Used This Month**: Current month's water consumption (m³)
- **Water Used Last Month**: Previous month's water consumption (m³)
- **Total Usage**: Cumulative total water consumption (m³) - *Energy Dashboard compatible*
- **Total Usage Hard Water**: Cumulative total hard water processed (m³)

#### ⚙️ System Status
- **Water Pressure**: Current water pressure (bar)
- **Remaining Capacity**: Remaining softening capacity (L)
- **Days Remaining**: Days until regeneration needed
- **Inbound Water Hardness**: Input water hardness (°fH)
- **Outbound Water Hardness**: Output water hardness (°fH)

#### 🔄 Regeneration Statistics
- **Last Regeneration**: Timestamp of last regeneration cycle
- **Normal Regenerations**: Count of normal regeneration cycles
- **Service Regenerations**: Count of service regeneration cycles
- **Incomplete Regenerations**: Count of incomplete regeneration cycles

### 🚦 Binary Sensors

- 🚨 **Alarm Active**: Indicates if an alarm is active
- ✅ **Connected**: Device connection status
- 🌐 **Network Connected**: Network connectivity status
- 🔄 **Regeneration Active**: Indicates if regeneration is in progress

## ⚡ Energy Dashboard

The integration is fully compatible with Home Assistant's Energy Dashboard:

1. Go to **Settings** → **Dashboards** → **Energy**
2. Click **Add Water Source** under the "Water" section
3. Select the **Total Usage** sensor
4. Save your configuration

The **Total Usage** sensor uses `TOTAL_INCREASING` state class, making it ideal for long-term tracking in the energy dashboard.

## 🔍 Troubleshooting

### 🔐 Session Expired Errors

The integration automatically handles session renewal. If authentication fails:

1. You'll receive a notification in Home Assistant
2. Go to **Settings** → **Devices & Services**
3. Click **Configure** on the Syr Oceanic integration
4. Re-enter your password
5. Click **Submit**

### ❓ Integration Not Found

If you can't find the integration after installation:

1. Ensure you've restarted Home Assistant after installation
2. Check the Home Assistant logs for errors
3. Verify the integration files are in `custom_components/syr_oceanic_ilex_connect/`

### 🔌 No Devices Found

If no devices appear after configuration:

1. Verify your credentials are correct
2. Check that your device is online in the i-Lex Connect portal
3. Check the integration logs for API errors

## 💬 Support

For issues, feature requests, or questions:
- 🐛 [Open an issue on GitHub](https://github.com/YOUR_USERNAME/YOUR_REPO/issues)

## 📄 License

This integration is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Thanks to Syr / Oceanic for their water softener products
- Built with ❤️ for the Home Assistant community

## ⚠️ Disclaimer

This integration is not officially affiliated with or endorsed by Syr or Oceanic. Use at your own risk.
