group "default" {
    targets = [
        "python-39-linux",
        "python-310-linux",
        "python-311-linux",
        "python-312-linux",
        "python-313-linux"
    ]
}

variable "DEBIAN_BASE" {
    default = "bullseye"
}

variable "GITHUB_ACTIONS" {
    default = false
}

target "shared" {
    dockerfile = ".github/docker/Dockerfile"
    cache-from = [
        GITHUB_ACTIONS ? "type=gha,scope=jpy-build" : ""
    ]
    cache-to = [
        GITHUB_ACTIONS ? "type=gha,mode=max,scope=jpy-build" : ""
    ]
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

target "python-312-linux" {
    inherits = [ "shared" ]
    args = {
        PYTHON_TAG = "3.12-${DEBIAN_BASE}"
    }
}

target "python-313-linux" {
    inherits = [ "shared" ]
    args = {
        PYTHON_TAG = "3.13-${DEBIAN_BASE}"
    }
}
