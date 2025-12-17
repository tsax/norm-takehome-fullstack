'use client';

import { Box, Spinner, Text } from '@chakra-ui/react';

export default function LoadingState() {
  return (
    <Box textAlign="center" py={8}>
      <Spinner size="lg" color="purple.500" />
      <Text mt={2} color="gray.500">
        Consulting the laws...
      </Text>
    </Box>
  );
}
