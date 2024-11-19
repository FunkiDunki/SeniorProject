import React, { useState } from "react";

function Adventure() {
  const [story, setStory] = useState({
    text: "You are standing at a crossroads. Type 'left' to go left or 'right' to go right.",
    choices: {
      left: "You head left and enter a dark forest.",
      right: "You head right and find a sunny meadow.",
    },
  });
  const [history, setHistory] = useState([]);
  const [userInput, setUserInput] = useState("");

  const handleInput = (event) => {
    if (event.key === "Enter") {
      const input = userInput.toLowerCase().trim();
      setHistory([...history, `> ${input}`]); // Add user input to history

      if (story.choices[input]) {
        // If the input matches a valid choice
        setHistory((prev) => [...prev, story.text]); // Add story text to history
        setStory({
          text: story.choices[input],
          choices: input === "left"
            ? {
                explore: "You find a mysterious hut.",
                back: "You return to the crossroads.",
              }
            : {
                relax: "You sit in the meadow and enjoy the sunshine.",
                back: "You return to the crossroads.",
              },
        });
      } else {
        // Invalid input
        setHistory((prev) => [...prev, "Invalid choice. Try again."]);
      }

      setUserInput(""); // Clear the input field
    }
  };

  return (
    <div id="app">
      <h1>The Legend of the Data Cube</h1>
      <p>{story.text}</p>
      <ul>
        {history.map((line, index) => (
          <li key={index}>{line}</li>
        ))}
      </ul>
      <input
        type="text"
        placeholder="Type your choice..."
        value={userInput}
        onChange={(e) => setUserInput(e.target.value)}
        onKeyDown={handleInput} // Listen for "Enter" key
        style={{
          width: "100%",
          padding: "10px",
          marginTop: "10px",
          fontSize: "16px",
          borderRadius: "5px",
        }}
      />
    </div>
  );
}

export default Adventure;
