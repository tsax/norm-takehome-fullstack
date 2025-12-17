'use client';

import { useState } from 'react';
import { Box, Text, Card, CardBody, VStack, Link } from '@chakra-ui/react';
import CitationList from './CitationList';

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

interface ResponseCardProps {
  result: QueryResponse;
}

// Parse response text and make citation references clickable
function renderResponseWithClickableCitations(
  response: string,
  citationCount: number,
  onCitationClick: (index: number) => void
) {
  // Match [1], [2], etc.
  const parts = response.split(/(\[\d+\])/g);

  return parts.map((part, i) => {
    const match = part.match(/^\[(\d+)\]$/);
    if (match) {
      const citationNum = parseInt(match[1], 10);
      // Only make clickable if citation exists (bounds check)
      if (citationNum >= 1 && citationNum <= citationCount) {
        return (
          <Link
            key={i}
            color="purple.600"
            fontWeight="bold"
            cursor="pointer"
            _hover={{ textDecoration: 'underline', color: 'purple.800' }}
            onClick={() => onCitationClick(citationNum - 1)}
            title={`Jump to source ${citationNum}`}
          >
            {part}
          </Link>
        );
      }
    }
    return <span key={i}>{part}</span>;
  });
}

export default function ResponseCard({ result }: ResponseCardProps) {
  const [expandedIndices, setExpandedIndices] = useState<number[]>([]);

  const handleCitationClick = (index: number) => {
    // Toggle the clicked citation
    setExpandedIndices((prev) => {
      if (prev.includes(index)) {
        return prev; // Already expanded, keep it
      }
      return [...prev, index];
    });

    // Scroll to citation
    setTimeout(() => {
      const element = document.getElementById(`citation-${index + 1}`);
      element?.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }, 100);
  };

  return (
    <Card>
      <CardBody>
        <VStack align="stretch" spacing={4}>
          <Box>
            <Text fontWeight="bold" color="gray.600" fontSize="sm">
              Your Question
            </Text>
            <Text>{result.query}</Text>
          </Box>

          <Box>
            <Text fontWeight="bold" color="gray.600" fontSize="sm">
              Answer
            </Text>
            <Text whiteSpace="pre-wrap">
              {renderResponseWithClickableCitations(
                result.response,
                result.citations.length,
                handleCitationClick
              )}
            </Text>
          </Box>

          <CitationList
            citations={result.citations}
            expandedIndices={expandedIndices}
            onToggle={setExpandedIndices}
          />
        </VStack>
      </CardBody>
    </Card>
  );
}
