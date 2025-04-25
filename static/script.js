document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("upload-btn").addEventListener("click", uploadFile);
});

function uploadFile() {
    let fileInput = document.getElementById("file-input");
    if (!fileInput.files.length) {
        alert("Please select a file!");
        return;
    }

    let formData = new FormData();
    formData.append("file", fileInput.files[0]);

    fetch("/upload", { method: "POST", body: formData })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                document.getElementById("progress-container").style.display = "block";
                trackProgress();
            }
        })
        .catch(error => console.error("Upload failed:", error));
}

function trackProgress() {
    let eventSource = new EventSource("/progress");
    eventSource.onmessage = function (event) {
        let progress = parseInt(event.data);
        document.getElementById("progress-bar").style.width = progress + "%";
        document.getElementById("progress-text").innerText = progress + "%";

        if (progress >= 100) {
            eventSource.close();
            fetchClips();
        }
    };
}

function fetchClips() {
    fetch("/get_clips")
        .then(response => response.json())
        .then(data => {
            let clipsContainer = document.getElementById("clips-container");
            let downloadButtons = document.getElementById("download-buttons");

            // Show container
            clipsContainer.style.display = "flex";

            // Clear previous buttons
            downloadButtons.innerHTML = "";

            // Add new download buttons
            data.clips.forEach(clip => {
                let link = document.createElement("a");
                link.href = "/clips/" + clip;
                link.innerText = `Download ${clip}`;
                link.classList.add("clip-download");
                link.setAttribute("download", clip);
                downloadButtons.appendChild(link);
            });
        })
        .catch(error => console.error("Error fetching clips:", error));
}