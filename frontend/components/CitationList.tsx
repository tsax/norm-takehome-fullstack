'use client';

import {
  Box,
  Text,
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon,
  Badge,
} from '@chakra-ui/react';

interface Citation {
  source: string;
  text: string;
  relevance_score: number;
}

interface CitationListProps {
  citations: Citation[];
  expandedIndices?: number[];
  onToggle?: (indices: number[]) => void;
}

// Color based on relevance score (with NaN safety)
function getRelevanceColor(score: number | undefined | null): string {
  const safeScore = typeof score === 'number' && !isNaN(score) ? score : 0;
  if (safeScore >= 0.8) return 'green';
  if (safeScore >= 0.6) return 'yellow';
  return 'orange';
}

// Format relevance score safely
function formatRelevanceScore(score: number | undefined | null): string {
  if (typeof score !== 'number' || isNaN(score)) return 'N/A';
  return `${Math.round(score * 100)}%`;
}

export default function CitationList({
  citations,
  expandedIndices = [],
  onToggle
}: CitationListProps) {
  if (citations.length === 0) return null;

  return (
    <Box>
      <Text fontWeight="bold" color="gray.600" fontSize="sm" mb={2}>
        Sources ({citations.length})
      </Text>
      <Accordion
        allowMultiple
        index={expandedIndices}
        onChange={(indices) => {
          // Chakra returns number | number[] - normalize to array
          const normalized = Array.isArray(indices) ? indices : [indices];
          onToggle?.(normalized);
        }}
      >
        {citations.map((citation, idx) => (
          <AccordionItem
            key={idx}
            id={`citation-${idx + 1}`}
            border="1px"
            borderColor="gray.200"
            borderRadius="md"
            mb={2}
          >
            <AccordionButton>
              <Box flex="1" textAlign="left" display="flex" alignItems="center">
                <Badge colorScheme="purple" mr={2}>
                  [{idx + 1}]
                </Badge>
                <Text as="span" mr={2}>{citation.source}</Text>
                <Badge
                  colorScheme={getRelevanceColor(citation.relevance_score)}
                  fontSize="xs"
                  title="Relevance score"
                >
                  {formatRelevanceScore(citation.relevance_score)} match
                </Badge>
              </Box>
              <AccordionIcon />
            </AccordionButton>
            <AccordionPanel pb={4} bg="gray.50">
              <Text fontSize="sm" color="gray.600">
                {citation.text}
              </Text>
            </AccordionPanel>
          </AccordionItem>
        ))}
      </Accordion>
    </Box>
  );
}
