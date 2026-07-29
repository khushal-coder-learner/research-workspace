import React from "react";
import { ChakraProvider, Box } from '@chakra-ui/react';
import MainLayout from './components/Layout/MainLayout';
import theme from './styles/theme';

function App() {
  return (
    <ChakraProvider theme={theme}>
      <Box height="100%" bg="gray.50">
        <MainLayout />
      </Box>
    </ChakraProvider>
  );
}

export default App;
