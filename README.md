# BabyHarvesterGateway

By: Jared Briskman, Eric Miller, Celina Bekins

This is the back-end server for a [Baby Harvester](https://github.com/HALtheWise/baby-harvester). The gateway serves as an API to communicate with (and develop applications for) the Baby Barvester platform, as well as the authentication service for each individual harvester.

![Deployment Diagram](/docs/img/deployment.png?raw=true)

## Deployment

To deploy your own gateway, just click the following:

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

It is recommended to provision a private MQTT broker. [CloudMQTT](https://www.cloudmqtt.com/) has a free-tier offering that is excellent for this purpose. Be sure to set the `MQTT_URL` environment variable appropriately prior to deployment.

More documentation can be found on the project wiki [here](https://github.com/HALtheWise/baby-harvester/wiki).
