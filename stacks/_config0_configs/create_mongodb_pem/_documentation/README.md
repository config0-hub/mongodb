# MongoDB SSL Keys Creation

## Description
This stack creates MongoDB SSL keys (mongodb.pem) for secure MongoDB server connections.

## Variables

### Required

| Name | Description | Default |
|------|-------------|---------|
| basename | Configuration for basename | |

## Features
- Creates SSL certificate files for MongoDB instances
- Generates mongodb.pem for secure connections

## Dependencies

### Shelloutconfigs
- [config0-publish:::mongodb::create_keys](https://api-app.config0.com/web_api/v1.0/assets/shelloutconfigs/config0-publish/mongodb/create_keys)

## License
Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.