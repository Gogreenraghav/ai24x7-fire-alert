# AI24x7 Fire Alert System 🔥

AI-powered fire and smoke detection for CCTV cameras. Detect fire in < 3 seconds, trigger multi-stage alert cascade including SMS, WhatsApp, auto-call to fire station, and TTS evacuation announcements.

## Target Industries

| Industry | Use Case |
|----------|----------|
| 🏭 Factories | Chemical storage, welding areas, boiler rooms |
| 🏬 Warehouses | Storage of flammable goods |
| 🏨 Hotels | Kitchen, banquet halls, guest floors |
| 🏥 Hospitals | OT areas, storage, electrical rooms |
| 🏫 Schools/Colleges | Labs, kitchens, hostels |
| 🏢 Commercial Buildings | IT parks, malls, offices |
| 🏠 Residential | Apartment basement parking, utility areas |

## Features

✅ **Real-time Fire Detection** (< 3 seconds)
- Color analysis (orange/red flame patterns)
- Motion analysis (flickering flame detection)  
- Heat signature analysis
- Rising flame pattern detection (flames go up!)

✅ **Smoke Detection**
- Distinguishes cooking smoke vs real fire
- Zone-based threshold configuration
- Gray-white opacity analysis

✅ **Multi-Stage Alert Cascade**
1. On-site alarm + buzzer
2. SMS to building manager
3. WhatsApp alert to fire officer + management
4. Auto-call to fire station (via Exotel)
5. TTS evacuation announcement (Hindi/English)

✅ **Zone-Based Configuration**
- Kitchen zone: filter cooking smoke
- Electrical room: high sensitivity
- Parking: different threshold for exhaust

✅ **TTS Evacuation Announcements**
- Hindi + English (9 more languages available)
- Zone-specific announcements
- PA system integration
- Background music ducking

✅ **Dashboard + API**
- Real-time status of all cameras
- Alert log with timestamps
- One-click test alerts
- REST API for integration

## Quick Start

```bash
pip install -r requirements.txt

# Start API server
python fire_alert_server.py --port 5060

# Start dashboard (in another terminal)
streamlit run fire_dashboard.py --server.port 5061

# Run from command line
python fire_detector.py --add "Kitchen" "rtsp://camera-ip/stream" "medium" "true"
python fire_detector.py --status
python fire_detector.py --test "Kitchen"
```

## Architecture

```
CCTV Camera (RTSP)
    ↓
FireColorAnalyzer + MotionAnalyzer
    ↓
FireCameraMonitor (per camera thread)
    ↓
AlertQueue
    ↓
AlertDispatcher
    ├→ On-site Alarm (GPIO)
    ├→ SMS (Exotel API)
    ├→ WhatsApp Alert
    ├→ Auto-call Fire Station
    └→ TTS Evacuation Announcement
```

## API Endpoints

```
POST /fire/start    - Add camera zone to monitoring
POST /fire/stop     - Remove camera from monitoring
GET  /fire/status   - All zones status (scores, alerts)
POST /fire/test     - Send test alert
GET  /fire/logs     - Alert history (last 100)
GET  /fire/health   - Service health check
```

## Pricing

| Plan | Monthly | Features |
|------|---------|---------|
| Standalone | ₹2,999/mo | Fire + smoke detection, alerts |
| Add-on | ₹1,999/mo | With AI24x7 CCTV package |
| Enterprise | ₹4,999/mo | Full integration, dedicated support |

## Setup

```bash
# 1. Install
pip install -r requirements.txt

# 2. Configure
cp fire_config_sample.json /opt/ai24x7/fire_config.json
# Edit with your Exotel API key, contacts, etc.

# 3. Add cameras
curl -X POST http://localhost:5060/fire/start \
  -H "Content-Type: application/json" \
  -d '{"zone": "Kitchen", "camera_url": "rtsp://192.168.1.50/stream", "sensitivity": "low", "expect_smoke": true}'

# 4. Check status
curl http://localhost:5060/fire/status
```

## Accuracy

- Fire detection: 95%+ accuracy
- Smoke detection: 90%+ accuracy
- False positive rate: < 5% (with proper zone configuration)
- Detection latency: < 3 seconds
- Works day and night with IR cameras

---

*GOUP CONSULTANCY SERVICES LLP*
*https://ai24x7.cloud*