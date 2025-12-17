'use client';

import { Box, Input, Button } from '@chakra-ui/react';

interface SearchInputProps {
  query: string;
  setQuery: (query: string) => void;
  onSubmit: (e: React.FormEvent) => void;
  isLoading: boolean;
}

export default function SearchInput({
  query,
  setQuery,
  onSubmit,
  isLoading,
}: SearchInputProps) {
  return (
    <form onSubmit={onSubmit}>
      <Box display="flex" gap={3}>
        <Input
          placeholder="e.g., What happens if I steal from a sept?"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          bg="white"
          size="lg"
          disabled={isLoading}
        />
        <Button
          type="submit"
          colorScheme="purple"
          size="lg"
          isLoading={isLoading}
          px={8}
        >
          Ask
        </Button>
      </Box>
    </form>
  );
}
