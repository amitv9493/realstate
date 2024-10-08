const token =
  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzI4NDcwNzMxLCJpYXQiOjE3MjgzODQzMzEsImp0aSI6IjMyMDdlMTkwN2M3ODQwOGQ4ZmZmOTAzYjMzMzdiYTNkIiwidXNlcl9pZCI6MX0.EF6vu0oOgERvV6lzOhupRCOTGr9EACmATqLB4sdS6ZU";

async function sendTaskData(jsonData, audioFile) {
  const url = "http://127.0.0.1:8000/api/task/showingtask/";

  const formData = new FormData();

  for (const [key, value] of Object.entries(jsonData)) {
    if (key === "property") {
      // For the property object, append each property field separately
      for (const [propKey, propValue] of Object.entries(value)) {
        formData.append(`property.${propKey}`, propValue);
      }
    } else {
      // For boolean values, convert them to strings
      formData.append(
        key,
        value === true ? "true" : value === false ? "false" : value
      );
    }
  }

  formData.append("audio_file", audioFile, audioFile.name);

  try {
    const response = await fetch(url, {
      method: "POST",
      body: formData,
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    console.log("Success:", result);
  } catch (error) {
    console.error("Error:", error);
  }
}

// The rest of your code remains the same
