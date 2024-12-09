const mindMapContainer = document.getElementById('mindMapContainer');

document.getElementById('mindMapFeature').addEventListener('click', function () {
    mindMapContainer.style.display = 'block'; // Show the mind map tool when selected
});

const mind = {
    "meta": {
        "name": "jsMind",
        "version": "1.2.0"
    },
    "format": "node_array",
    "data": [
        {
            "id": "root",
            "topic": "Mind Map",
            "children": [
                { "id": "sub1", "topic": "Subtopic 1" },
                { "id": "sub2", "topic": "Subtopic 2" }
            ]
        }
    ]
};

const options = {
    container: 'jsmind',
    editable: true,
    theme: 'default'
};

const jm = new jsMind(options);
jm.set_data(mind);

document.getElementById('saveMindMapBtn').addEventListener('click', function () {
    const mindMapData = jm.get_data();
    document.getElementById('mindMapOutput').innerText = JSON.stringify(mindMapData, null, 2);
    // Here you can send the mind map data to the server for saving or processing
});