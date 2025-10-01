group "default" {
    targets = [
        "python-39-linux",
    ]
}

variable "DEBIAN_BASE" {
    # bullseye: manylinux2014 / manylinux_2_17
    # bookworm: manylinux_2_34
    # trixie: Unable to build on Debian trixie, https://github.com/jpy-consortium/jpy/issues/202
    default = "trixie"
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
