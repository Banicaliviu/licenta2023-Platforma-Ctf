# Implement docker_push, docker_pull, remove_image, update_image, list_images, get_image(imageName), add_tag, get_image_digest, form_url,
from ctfplatform.utils import append_new_line
import docker


# build and push and check logs now, moved client=docker.from_env() to try statement to see the error
# go black .
def docker_pull(imageName):
    try:
        client = docker.from_env()
        client.images.pull(imageName)
        append_new_line("logs.txt", f"Image {imageName} pulled successfully ")
        return True
    except docker.errors.APIError as e:
        append_new_line("logs.txt", f"Error at pulling image {imageName}: {e}")
        return False


def updateImageTag(imageName, tag):
    append_new_line("logs.txt", f"Updating image {imageName} tag...")
    append_new_line("logs.txt", f"Tag to be added {tag} tag...")

    new_imageName = f"{tag}/{imageName}"
    append_new_line("logs.txt", f"Image updated: {new_imageName}")
    return new_imageName


def docker_push(imageName):
    client = docker.from_env()
    try:
        client.images.push(imageName)
        append_new_line("logs.txt", f"Image {imageName} pushed successfully ")
        return True
    except docker.errors.APIError as e:
        append_new_line("logs.txt", f"Error at pushing image {imageName}: {e}")
        return False


# updateChart_deployment_imageName(helm_package_path, imageName) will update the imageName from Values.yaml so the Chart uses the recently pushed image to ctfplatform's image registry repository
