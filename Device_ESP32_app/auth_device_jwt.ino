Preferences prefs;
String jwtToken;
unsigned long tokenExpEpoch = 0; // opcional si devuelves exp

bool fetchDeviceToken() {
  WiFiClientSecure client;
  client.setInsecure(); // TODO: usar CA real con client.setCACert(...)
  HTTPClient https;
  if (!https.begin(client, serverUrl + "/auth/device")) return false;
  https.addHeader("Content-Type", "application/json");

  StaticJsonDocument<256> doc;
  doc["device_id"] = deviceId;
  doc["api_key"]   = apiKey;
  String body; serializeJson(doc, body);

  int code = https.POST(body);
  if (code != 200) { https.end(); return false; }
  DynamicJsonDocument res(512);
  DeserializationError err = deserializeJson(res, https.getStream());
  https.end();
  if (err) return false;

  jwtToken = res["access_token"].as<String>();
  // opcional: tokenExpEpoch = now + res["expires_in"].as<int>();
  prefs.begin("auth", false);
  prefs.putString("jwt", jwtToken);
  prefs.end();
  return jwtToken.length() > 0;
}

String ensureToken() {
  if (jwtToken.length() > 0) return jwtToken;
  prefs.begin("auth", true);
  jwtToken = prefs.getString("jwt", "");
  prefs.end();
  if (jwtToken.length() == 0) {
    fetchDeviceToken();
  }
  return jwtToken;
}