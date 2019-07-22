//
//  ViewController.swift
//  ev3_mqtt
//
//  Created by Kevin Chen on 6/11/2019.
//  Copyright © 2019 New York University. All rights reserved.
//

import UIKit
import CocoaMQTT
import Speech

class ViewController: UIViewController {
    
    var mqtt: CocoaMQTT!
    @IBOutlet weak var connectionLabel: UILabel!
    
    override func viewDidLoad() {
        super.viewDidLoad()
        setUpMQTT()
    }
    
    @IBAction func onTap(_ sender: Any) {
        view.endEditing(true)
    }
    
    func setUpMQTT() {
        let clientID = "CocoaMQTT-" + String(ProcessInfo().processIdentifier)
        print("Hello")
        mqtt = CocoaMQTT(clientID: clientID, host: "192.168.1.102", port: 1883)
        print(clientID)
        mqtt.username = "nyu"
        mqtt.password = "nyu"
        mqtt.willMessage = CocoaMQTTWill(topic: "/will", message: "dieout")
        mqtt.keepAlive = 60
        mqtt.delegate = self
        mqtt.connect()
    }
    
    @IBAction func get_position(_ sender: Any) {
        mqtt.publish("tag/iosaction", withString: "Position 1")
    }
    
    @IBAction func draw_square(_ sender: Any) {
        mqtt.publish("tag/iosaction", withString: "Draw Square")
    }
    
    @IBAction func draw_triangle(_ sender: Any) {
        mqtt.publish("tag/iosaction", withString: "Draw Triangle")
    }
    
    @IBAction func draw_circle(_ sender: Any) {
        mqtt.publish("tag/iosaction", withString: "Draw Circle")
    }
    
    @IBAction func goDown(_ sender: Any) {
        mqtt.publish("tag/iosaction", withString: "Move Down")
    }
    
    @IBAction func goUp(_ sender: Any) {
        mqtt.publish("tag/iosaction", withString: "Move Up")
    }
    
    @IBAction func goLeft(_ sender: Any) {
        mqtt.publish("tag/iosaction", withString: "Rotate Left")
    }
    
    @IBAction func goRight(_ sender: Any) {
        mqtt.publish("tag/iosaction", withString: "Rotate Right")
    }
    
    // Shortcut to read
    func say(item: Any) { // Speech
        SpeechService.shared.speak(text: "\(item as! String)", voiceType: .waveNetFemale) { }
    }
}

extension ViewController: CocoaMQTTDelegate {
    // These two methods are all we care about for now
    func mqtt(_ mqtt: CocoaMQTT, didReceiveMessage message: CocoaMQTTMessage, id: UInt16 ) {
        if let msgString = message.string {
            self.say(item: msgString)
        }
    }
    
    // Other required methods for CocoaMQTTDelegate
    func mqtt(_ mqtt: CocoaMQTT, didReceive trust: SecTrust, completionHandler: @escaping (Bool) -> Void) {
        completionHandler(true)
    }
    
    func mqtt(_ mqtt: CocoaMQTT, didConnectAck ack: CocoaMQTTConnAck) {
        connectionLabel.text = "Connected"
        connectionLabel.textColor = UIColor.green
        self.mqtt.subscribe("tag/iosspeak")
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

