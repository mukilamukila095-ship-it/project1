function generateBlueprint() {
    console.log("Generating Blueprint with Plot Size...");

    const getVal = (id, defaultVal) => {
        const el = document.getElementById(id);
        return el ? el.value : defaultVal;
    };

    // Plot Size மற்றும் பிற விவரங்களைப் பெறுதல்
    const plotSize = getVal("plotSize", "30x40 ft");
    const bedrooms = getVal("bedrooms", 2);
    const bathrooms = getVal("bathrooms", 2);
    const parking = getVal("parking", "Yes");
    const balcony = getVal("balcony", "Yes");
    const garden = getVal("garden", "Yes");
    const pooja = getVal("pooja", "Yes");
    const study = getVal("study", "Yes");

    // 1. Plot Size சேர்க்கப்பட்ட 2D CAD Blueprint Prompt
    const prompt2D = encodeURIComponent(
        `architectural 2d floor plan blueprint, exact plot dimensions ${plotSize}, top-down schematic layout, crisp sharp CAD lines, ${bedrooms} bedrooms, ${bathrooms} bathrooms, living hall, kitchen, ${parking === 'Yes' ? 'car parking garage' : ''}, ${garden === 'Yes' ? 'garden space' : ''}, detailed dimension lines, white background, high resolution`
    );

    // 2. Plot Size சேர்க்கப்பட்ட 3D Isometric Cutaway Prompt
    const prompt3D = encodeURIComponent(
        `3d isometric cutaway floor plan render, open top-down house layout for plot size ${plotSize}, fully furnished, ${bedrooms} bedrooms, ${bathrooms} bathrooms, living hall, kitchen, ${parking === 'Yes' ? 'garage with car' : ''}, realistic architectural 3d plan`
    );

    const randomSeed = Math.floor(Math.random() * 99999);
    
    // Pollinations AI Image URLs
    const aiImage2D = `https://image.pollinations.ai/prompt/${prompt2D}?width=1024&height=1024&seed=${randomSeed}&nologo=true`;
    const aiImage3D = `https://image.pollinations.ai/prompt/${prompt3D}?width=1024&height=1024&seed=${randomSeed + 1}&nologo=true`;

    const formData = {
        project_name: "My Dream Home",
        plot_size: plotSize,
        bedroom: parseInt(bedrooms),
        bathrooms: parseInt(bathrooms),
        parking: parking,
        balcony: balcony,
        garden: garden,
        pooja: pooja,
        study: study,
        image_2d: aiImage2D,
        image_3d: aiImage3D
    };

    // FastAPI Backend-க்கு அனுப்புதல்
    fetch('http://127.0.0.1:8000/api/select-rooms', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === "success") {
            window.location.href = "save.html";
        } else {
            alert("Error: " + (data.message || "Failed to generate plan"));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert("Failed to connect to backend!");
    });
}