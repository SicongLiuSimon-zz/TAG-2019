After setting up MQTT server on backpack:
Website Source for MQTT in iOS: https://medium.com/thefloatingpoint/mqtt-in-ios-d8574b55e006
1) Cocoa Pod: Install CocoaMQTT (pod init, pod CocoaMQTT, pod install)
2) Setup Function (add in viewcontroller.swift)
```
var mqtt: CocoaMQTT!
override func viewDidLoad() {
    super.viewDidLoad()
    setUpMQTT()
}
```
```
func setUpMQTT() {
    let clientID = "CocoaMQTT-" + String(ProcessInfo().processIdentifier)
    mqtt = CocoaMQTT(clientID: clientID, host: "localhost", port: 1883)
    mqtt.username = "test"
    mqtt.password = "public"
    mqtt.willMessage = CocoaMQTTWill(topic: "/will", message: "dieout")
    mqtt.keepAlive = 60
    mqtt.connect()
}
```
3) Add extension/delgate functions
* didConnectAck is called when the connection to MQTT server is successful
```
extension ViewController: CocoaMQTTDelegate {
    // These two methods are all we care about for now
    func mqtt(_ mqtt: CocoaMQTT, didConnect host: String, port: Int) {
    }
    
    func mqtt(_ mqtt: CocoaMQTT, didReceiveMessage message: CocoaMQTTMessage, id: UInt16 ) {
    }
    
    // Other required methods for CocoaMQTTDelegate
    func mqtt(_ mqtt: CocoaMQTT, didReceive trust: SecTrust, completionHandler: @escaping (Bool) -> Void) {
        completionHandler(true)
    }
    
    func mqtt(_ mqtt: CocoaMQTT, didConnectAck ack: CocoaMQTTConnAck) {
        // CODE FOR SUCCESSFUL CONNECTION
    }
    
    func mqtt(_ mqtt: CocoaMQTT, didPublishMessage message: CocoaMQTTMessage, id: UInt16) {
    }
    
    func mqtt(_ mqtt: CocoaMQTT, didPublishAck id: UInt16) {
    }
    
    func mqtt(_ mqtt: CocoaMQTT, didSubscribeTopic topic: String) {
    }
    
    func mqtt(_ mqtt: CocoaMQTT, didUnsubscribeTopic topic: String) {
    }
    
    func mqttDidPing(_ mqtt: CocoaMQTT) {
    }
    
    func mqttDidReceivePong(_ mqtt: CocoaMQTT) {
    }
    
    func mqttDidDisconnect(_ mqtt: CocoaMQTT, withError err: Error?) {
    }
    
    func _console(_ info: String) {
    }
}
```