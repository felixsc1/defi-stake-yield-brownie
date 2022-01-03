import React from 'react';
import {DAppProvider, ChainId} from "@usedapp/core"
import {Header} from "./components/Header"
// Containers are the most basic element, to center content horizontally https://mui.com/components/container/
import {Container} from "@material-ui/core"


function App() {
  return (
    <DAppProvider config={{
      supportedChains: [ChainId.Kovan, ChainId.Rinkeby]
      }}>
        <Header />
        {/*  Below the header we place a container with "medium" width */}
        <Container maxWidth="md">
          <div>Hello World!</div>
        <Container/>
    </DAppProvider>
  );
}

export default App;
