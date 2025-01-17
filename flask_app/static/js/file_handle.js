document.addEventListener('DOMContentLoaded', () => {
    let base64Image;
    //convert the image file to base64 when selected:
    document.getElementById("image-selector").addEventListener("change", function () {
        const reader = new FileReader();
        reader.onload = function (event) {
            const dataURL = event.target.result;
            document.getElementById("selected-image").src = dataURL;
            base64Image = dataURL.replace(/^data:image\/(png|jpg|jpeg);base64,/, "");
            //clear previous predictions:
            document.getElementById("glioma_tumor_prediction").textContent = "";
            document.getElementById("meningioma_tumor_prediction").textContent = "";
            document.getElementById("no_tumor_prediction").textContent = "";
        };
        reader.readAsDataURL(this.files[0]);
    });
// Handle Predict button click
    document.getElementById("predict-button").addEventListener("click", () => {
        if (!base64Image) {
            alert("Please upload an image first!");
            return;
        }

        const message = { image: base64Image };

        // Send POST request to Flask API
        fetch("https://brain-tumor-prediction-y0vx.onrender.com/tumor_predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(message),
        })
            .then(response => response.json())
            .then(data => {
                // Update the predictions
                document.getElementById("glioma_tumor_prediction").textContent = data.Prediction.glioma_tumor;
                document.getElementById("meningioma_tumor_prediction").textContent = data.Prediction.meningioma_tumor;
                document.getElementById("no_tumor_prediction").textContent = data.Prediction.no_tumor;
            })
            .catch(error => console.error("Error:", error));
    });
});
