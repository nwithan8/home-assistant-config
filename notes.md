Blueprints:

i.e. for a script
- input is something that will be tied to that script (once set when making the script, it's locked) (configuration)
- field is something that is passed into the script when it's called (runtime variable)
Ex. I want this script to update this particular device with a number - device would be an input, number would be a field

Selector actions can't be used as fields, only as inputs
https://community.home-assistant.io/t/use-input-fields-in-script-as-sequences/452683/9?u=nwithan8

Domains:
https://community.home-assistant.io/t/list-of-all-domains-entities/148059/6?u=nwithan8

- Recommended to redeclare all inputs as variables for a script run
- Actions can't be converted to variables, have to be referred to by !input name


Automation vs script
- Having an automation call just a script is bad design
- Scripts are meant for processing different input. If the input never changes, just use an automation


Mini Split
- combo of heat/cool/fan + high/low/powerful/2-hour (med)/9-hour (med)