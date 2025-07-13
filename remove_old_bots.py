#!/usr/bin/env python3
import yaml

# Read the docker-compose.yml file
with open('docker-compose.yml', 'r') as f:
    compose_data = yaml.safe_load(f)

# Remove old bot services
services_to_remove = ['rewrite-bot', 'intent-bot']
for service in services_to_remove:
    if service in compose_data['services']:
        del compose_data['services'][service]
        print(f"Removed {service} from docker-compose.yml")

# Update backend dependencies to remove old bots
if 'backend' in compose_data['services']:
    backend = compose_data['services']['backend']
    if 'depends_on' in backend:
        # Remove old bots from dependencies
        for bot in services_to_remove:
            if bot in backend['depends_on']:
                del backend['depends_on'][bot]
                print(f"Removed {bot} from backend dependencies")

# Write back the updated docker-compose.yml
with open('docker-compose.yml', 'w') as f:
    yaml.dump(compose_data, f, default_flow_style=False, sort_keys=False)

print("Updated docker-compose.yml successfully")