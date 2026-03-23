import React, {useState} from 'react';

/**
 * Counter Component - A simple counter with increment and decrement functionality
 * Uses React functional component with useState hook
 */
const Counter = ({ initialValue = 0, step = 1 }) => {
  // State to store the current count value
  const [count, setCount] = useState(initialValue);

  // Function to increment the counter
  const increment = () => {
    setCount(prevCount => prevCount + step);
  };

  // Function to decrement the counter
  const decrement = () => {
    setCount(prevCount => prevCount - step);
  };

  // Function to reset counter to initial value
  const reset = () => {
    setCount(initialValue);
  };

  return (
    <div className="counter-container" style={styles.container}>
      <h2 style={styles.title}>React Counter</h2>

      {/* Display the current count */}
      <div style={styles.display}>
        <span style={styles.count}>{count}</span>
      </div>

      {/* Control buttons */}
      <div style={styles.buttonContainer}>
        <button
          onClick={decrement}
          style={{...styles.button, ...styles.decrementButton}}
          aria-label="Decrease count"
        >
          -
        </button>

        <button
          onClick={reset}
          style={{...styles.button, ...styles.resetButton}}
          aria-label="Reset count"
        >
          Reset
        </button>

        <button
          onClick={increment}
          style={{...styles.button, ...styles.incrementButton}}
          aria-label="Increase count"
        >
          +
        </button>
      </div>

      {/* Additional information */}
      <div style={styles.info}>
        <p>Step size: {step}</p>
        <p>Initial value: {initialValue}</p>
      </div>
    </div>
  );
};

// Inline styles for the component
const styles = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    padding: '20px',
    border: '2px solid #00ffff',
    borderRadius: '15px',
    background: 'rgba(10, 10, 20, 0.9)',
    boxShadow: '0 0 20px rgba(0, 255, 255, 0.3)',
    maxWidth: '300px',
    margin: '20px auto',
    fontFamily: 'Courier New, monospace',
    color: '#00ffff',
  },
  title: {
    fontSize: '1.5rem',
    marginBottom: '20px',
    textShadow: '0 0 10px #00ffff',
    color: '#ff00ff',
  },
  display: {
    marginBottom: '20px',
  },
  count: {
    fontSize: '3rem',
    fontWeight: 'bold',
    color: '#00ffff',
    textShadow: '0 0 20px #00ffff',
  },
  buttonContainer: {
    display: 'flex',
    gap: '10px',
    marginBottom: '20px',
  },
  button: {
    padding: '10px 15px',
    border: 'none',
    borderRadius: '8px',
    fontSize: '1.2rem',
    fontWeight: 'bold',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    minWidth: '60px',
  },
  decrementButton: {
    background: '#ff4444',
    color: 'white',
    boxShadow: '0 0 10px rgba(255, 68, 68, 0.5)',
  },
  resetButton: {
    background: '#888888',
    color: 'white',
    boxShadow: '0 0 10px rgba(136, 136, 136, 0.5)',
  },
  incrementButton: {
    background: '#44ff44',
    color: 'white',
    boxShadow: '0 0 10px rgba(68, 255, 68, 0.5)',
  },
  info: {
    fontSize: '0.9rem',
    opacity: 0.8,
    textAlign: 'center',
  },
};

// Default props
Counter.defaultProps = {
  initialValue: 0,
  step: 1,
};

export default Counter;
