'use client';

import { useParams } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { Card, Table } from 'react-bootstrap';
import Layout from '../../../../components/Layout';
import { api } from '../../../../lib/api';

interface ItemStat {
  item: number;
  difficulty: number;
  discrimination_index: number;
  point_biserial: number;
}

interface AnalyticsResponse {
  exam_id: number;
  kr20: number;
  average_score: number;
  average_percent: number;
  item_stats: ItemStat[];
}

export default function AnalyticsPage() {
  const params = useParams<{ id: string }>();
  const examId = params.id;

  const query = useQuery({
    queryKey: ['analytics', examId],
    queryFn: async () => {
      const res = await api.get(`/analysis/exams/${examId}/`);
      return res.data as AnalyticsResponse;
    }
  });

  return (
    <Layout>
      <h1>Analytics</h1>
      {query.data && (
        <>
          <div className="d-flex gap-3 mb-3">
            <Card>
              <Card.Body>
                <Card.Title>Average Score</Card.Title>
                <Card.Text>{query.data.average_score}</Card.Text>
              </Card.Body>
            </Card>
            <Card>
              <Card.Body>
                <Card.Title>Average Percent</Card.Title>
                <Card.Text>{query.data.average_percent}%</Card.Text>
              </Card.Body>
            </Card>
            <Card>
              <Card.Body>
                <Card.Title>KR-20</Card.Title>
                <Card.Text>{query.data.kr20}</Card.Text>
              </Card.Body>
            </Card>
          </div>
          <Table bordered hover>
            <thead>
              <tr>
                <th>Item</th>
                <th>Difficulty</th>
                <th>Discrimination Index</th>
                <th>Point-Biserial</th>
              </tr>
            </thead>
            <tbody>
              {query.data.item_stats.map((stat) => (
                <tr key={stat.item}>
                  <td>{stat.item}</td>
                  <td>{stat.difficulty.toFixed(2)}</td>
                  <td>{stat.discrimination_index.toFixed(2)}</td>
                  <td>{stat.point_biserial.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </Table>
        </>
      )}
    </Layout>
  );
}
