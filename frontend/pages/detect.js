import { useState } from "react";

export default function DetectPeople() {
    const [file, setFile] = useState(null);
    const [peopleCount, setPeopleCount] = useState(null);
    const [imageUrl, setImageUrl] = useState(null);
    const [loading, setLoading] = useState(false);
    const [errorMessage, setErrorMessage] = useState(null); // To store any error messages
    const API_URL = `${process.env.NEXT_PUBLIC_API_URL}/detect/`;

    const handleFileChange = (event) => {
        setFile(event.target.files[0]);
        setErrorMessage(null); // Reset error message when a new file is selected
    };

    const handleUpload = async () => {
        if (!file) {
            setErrorMessage("Please select a file!");  // Display message if no file is selected
            return;
        }

        setLoading(true);
        const formData = new FormData();
        formData.append("file", file);

        try {
            const response = await fetch(API_URL, {
                method: "POST",
                body: formData,
            });

            // If the server returns an error (status not 2xx)
            if (!response.ok) {
                const errorData = await response.json();
                setErrorMessage(errorData?.detail || "Failed to process image!");  // Display server error message (detail)
                return;
            }

            const data = await response.json();
            setPeopleCount(data.people_count);
            setImageUrl(data.visualized_image_path);
        } catch (error) {
            console.error("Error:", error);
            setErrorMessage(error.message || "Failed to process image!");  // Handle and display unexpected errors
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="container">
            <h1 style={{ color: "#2462CE" }}>Detect People in Your Image</h1>

            <div className="card">
                <input
                    type="file"
                    accept="image/*"
                    onChange={handleFileChange}
                />
                <button
                    onClick={handleUpload}
                    disabled={!file || loading}
                >
                    {loading ? "Processing..." : "Upload & Detect"}
                </button>
            </div>

            {errorMessage && (
                <div style={{ color: "red", marginTop: "10px" }}>
                    <p>{errorMessage}</p>
                </div>
            )}

            {peopleCount !== null && (
                <div className="card" style={{ textAlign: "center" }}>
                    <p
                        style={{
                            color: "#C68B17",
                            marginBottom: "24px", // Increase the space below the paragraph
                            fontSize: "2rem", // Increase the font size
                            fontWeight: "bold", // Optional: Make the text bold
                        }}
                    >
                        People Count: {peopleCount}
                    </p>
                    {imageUrl && (
                        <img
                            src={imageUrl}
                            alt="Processed Image"
                            style={{
                                display: "block",
                                margin: "0 auto", // Centers the image horizontally
                                width: "1024px",   // Set width to 1024px
                                height: "1024px",  // Set height to 1024px
                                objectFit: "cover" // Maintain the aspect ratio of the image
                            }}
                        />
                    )}
                </div>
            )}
        </div>
    );
}