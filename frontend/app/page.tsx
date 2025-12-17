'use client';

import { useState } from 'react';
import { Box, Container, VStack, Text, Heading } from '@chakra-ui/react';
import HeaderNav from '@/components/HeaderNav';
import SearchInput from '@/components/SearchInput';
import ResponseCard from '@/components/ResponseCard';
import LoadingState from '@/components/LoadingState';
import ErrorAlert from '@/components/ErrorAlert';

interface Citation {
  source: string;
  text: string;
  relevance_score: number;
}

interface QueryResponse {
  query: string;
  response: string;
  citations: Citation[];
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function Page() {
  const [query, setQuery] = useState('');
  const [result, setResult] = useState<QueryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);  // Clear old result to avoid showing stale data with new error

    try {
      const res = await fetch(
        `${API_URL}/query?q=${encodeURIComponent(query)}`
      );

      if (!res.ok) {
        const errorData = await res.json().catch(() => null);
        throw new Error(
          errorData?.detail || `Server error: ${res.status}`
        );
      }

      const data = await res.json();
      setResult(data);
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Failed to connect to the API. Make sure the backend is running.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box minH="100vh" bg="gray.50">
      <HeaderNav signOut={() => {}} />

      <Container maxW="4xl" py={8}>
        <VStack spacing={6} align="stretch">
          <Box textAlign="center" mb={4}>
            <Heading size="lg" color="gray.700">
              Laws of the Seven Kingdoms
            </Heading>
            <Text color="gray.500" mt={2}>
              Ask questions about Westeros law in natural language
            </Text>
          </Box>

          <SearchInput
            query={query}
            setQuery={setQuery}
            onSubmit={handleSubmit}
            isLoading={loading}
          />

          {error && <ErrorAlert message={error} />}

          {loading && <LoadingState />}

          {result && !loading && <ResponseCard result={result} />}
        </VStack>
      </Container>
    </Box>
  );
}
