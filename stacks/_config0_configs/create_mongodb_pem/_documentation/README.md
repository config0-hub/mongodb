**Description**

 - This stack generates the MongoDB PEM file required for establishing a self-signed SSL connection.

**Required**

| argument      | description                                | var type | default      |
| ------------- |--------------------------------------------| -------- | ------------ |
| basename   | the basename for the mongodb hostname [^1] | string   | None         |

[^1]: e.g. The basename for dev-mongodb-01, dev-mongodb-02, dev-mongodb-03 is: __dev-mongodb__
