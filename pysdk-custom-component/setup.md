# Creating a custom component using the python-sdk

1. Implement the component by subclassing a `component` from the python-sdk
2. Add your custom component(s) to the python server and start the server
3. Connect your server to the RDK as a remote
4. ...
5. Profit

## Remotes
```json
[
  {
    "address": "localhost:9090",
    "insecure": true,
    "name": "python-controller"
  }
]
```

## Processes
```json
[
  {
    "args": [
      "-u",
      "njooma",
      "/home/njooma/viam/bin/python",
      "/home/njooma/python-sdk/controller.py"
    ],
    "id": "1",
    "log": true,
    "name": "sudo"
  }
]
```
