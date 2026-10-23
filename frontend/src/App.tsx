import React from 'react';
import { ChartForm } from './components/ChartForm';

function App() {
  return (
    <div style={styles.app}>
      <ChartForm />
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  app: {
    minHeight: '100vh',
  },
};

export default App;