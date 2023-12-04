# PROJET DRONE - MIA OP - Gr1

## Membres - Groupe 1

- Teddy BARTHELEMY
- Jose LUAMBA-WAFUANA
- Gabriel PERROTIN
- Augustin BAUDRY

## Classe personnalisée

Le fichier [dronekit_wrapper.py](https://github.com/Ted240/Projet_Drone/blob/master/dronekit_wrapper.py) contient un wrapper pour le module dronekit afin d'implémenter plus facilement un fonctionnement avec Mission Planner.
Des permissions administratives sont requises

### Installation

Téléchargez le fichier [dronekit_wrapper.py](https://github.com/Ted240/Projet_Drone/blob/master/dronekit_wrapper.py) et placez-le à côté de votre script principal.
Insérez au debut de votre script principal `import dronekit_wrapper` afin de pouvoir l'utiliser.

### Utilisation

Créer l'objet drone :<br>
`<NOM_DE_VARIABLE> = dronekit_wrapper.Drone(<LATITUDE>, <LONGITUDE>, <IP>, <?PORT>)`

Fait décoller le drone à 20m d'altitude :<br>
`drone.arm_and_takeoff(20)`

Distance entre le drone et le prochain point à visiter :<br>
`drone.waypoint_distance`

...

### Commandes

#### Méthodes
- `Drone(<LATITUDE>, <LONGITUDE>, <IP>, <?PORT>)`
- `Drone.arm_and_takeoff(<ALTITUDE>)`
- `Drone.create_mission()`
- `Drone.add_waypoint(<LATITUDE>, <LONGITUDE>, <?ALTITUDE>)`
- `Drone.start_mission()`
- `Drone.land()`
- `Drone.stop()`

#### Attributs
- `Drone.connection_string`
- `Drone.is_armed`
- `Drone.next_waypoint`
- `Drone.has_finished`
- `Drone.is_returning`
- `Drone.home_distance`
- `Drone.waypoint_distance`
- `Drone.start`*
- `Drone.default_alt`*
- `Drone.vehicle`*

*Attributs peu utilisés

**N'hésitez pas à lire la documentation de chaque fonction ou à vous inspirer du fichier [main.py](https://github.com/Ted240/Projet_Drone/blob/master/main.py) (en bas)**
