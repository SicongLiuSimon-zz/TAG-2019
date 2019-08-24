# TAG

<img src="tag-2019.png" width=1000><br>

## Information
  * Various Aspects of TAG:
    * EV3 Robot
    * MQTT Server
    * iOS App
    * OptiTrack, Motive Software, NatNet SDK
  * Important Folders:
    * Motion Capture Test
      * One File: stream_from_optitrack.py (steams data from OptiTrack to MQTT: tag/optitrack_data)
    * iOS TAG Project
      * iOS App: has user interface and commands to EV3 Robot through MQTT (tag/networktest)
  * App Design
    * Up, Down, Left, Right Arrow Keys: moving & turning
    * EV3 Robot Button: say current robot position & stop current robot action
    * Slider: adjust for moving length and shape length
    * Shapes: Draw each Shapes
    * Grid: Tap to command robot to move to tapped coordinate point
  * OptiTrack Structure
    * Two Rigid Bodies:
      * 1: EV3 Robot
      * 2: Activity "Toy" to create interactive learning
    * Orientation
      * 0 degrees is positive x-axis
      * 90 degrees is positive y-axis
      * 180 degrees is negative x-axis
      * 270 degrees is negative y-axis
  * Code Structure
    * Loop: OptiTrack -> MQTT -> iOS App -> EV3 Robot
    * Threads:
      * OptiTrack: Streaming data from Motive to MQTT (tag/optitrack_data)
      * Action: iOS App sends commands to EV3 Robot through MQTT (tag/networktest)
    * Actions are performed in a queue sequence. When the user presses on a button, the function is put on a queue, waiting for the previous function to finish before it is called. Two Queues: 1 function, 1 parameters
      * Queue Format, example: Function [1, 3, 1, 2] & Parameters [90, 4, (4,3), 270, 1]
        * Function: 1-Move, 2-Turn, 3-moveTo, 4-draw_square, 5-draw_triangle
        * Parameters: Int(length), Double(orientation), Tuple(coordinate pair)

## From Scratch
1. Clone this repository to laptop and OptiTrack Desktop
2. Sideload iOS app (iOS TAG Project folder) onto iPad through Xcode
3. Load MQTT Test folder onto EV3 robot through VSC (https://sites.google.com/site/ev3devpython/setting-up-vs-code)
4. Run stream_from_optitrack.py on the OptiTrack Desktop
5. Run iOS app on iPad
