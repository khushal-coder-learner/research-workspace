import React from "react";
import { Flex } from '@chakra-ui/react';
import LLMStatus from './LLMStatus';

const Header = () => (
  <Flex as="header" align="center" p={4} boxShadow="sm" bg="white" zIndex={10} justify="space-between">
    <LLMStatus />
  </Flex>
);

export default Header;
