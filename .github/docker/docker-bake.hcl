group "default" {
    targets = [
        "python-36-linux",
        "python-37-linux",
        "python-38-linux",
        "python-39-linux",
        "python-310-linux",
        "python-311-linux"
    ]
}

variable "DEBIAN_BASE" {
    default = "bullseye"
}

target "shared" {
    dockerfile = ".github/docker/Dockerfile"
}

target "python-36-linux" {
    inherits = [ "shared" ]
    args = {
        PYTHON_TAG = "3.6-${DEBIAN_BASE}"
    }
}

target "python-37-linux" {
    inherits = [ "shared" ]
    args = {
        PYTHON_TAG = "3.7-${DEBIAN_BASE}"
    }
}

target "python-38-linux" {
    inherits = [ "shared" ]
    args = {
        PYTHON_TAG = "3.8-${DEBIAN_BASE}"
    }
}

target "python-39-linux" {
    inherits = [ "shared" ]
    args = {
        PYTHON_TAG = "3.9-${DEBIAN_BASE}"
    }
}

target "python-310-linux" {
    inherits = [ "shared" ]
    args = {
        PYTHON_TAG = "3.10-${DEBIAN_BASE}"
    }
}

target "python-311-linux" {
    inherits = [ "shared" ]
    args = {
        PYTHON_TAG = "3.11-${DEBIAN_BASE}"
    }
}
