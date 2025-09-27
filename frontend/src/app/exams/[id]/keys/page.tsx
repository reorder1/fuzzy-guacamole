'use client';

import { useParams } from 'next/navigation';
import { useMutation, useQuery } from '@tanstack/react-query';
import { Button, Form, Table } from 'react-bootstrap';
import { useState } from 'react';
import Layout from '../../../../components/Layout';
import { api } from '../../../../lib/api';

interface ExamSet {
  id: number;
  set_code: string;
  answer_key: string[];
}

export default function AnswerKeysPage() {
  const params = useParams<{ id: string }>();
  const examId = params.id;
  const [setCode, setSetCode] = useState('A');
  const [keyInput, setKeyInput] = useState('A,B,C,D');

  const query = useQuery({
    queryKey: ['exam-sets', examId],
    queryFn: async () => {
      const res = await api.get('/exam-sets/', { params: { exam: examId } });
      return res.data as ExamSet[];
    }
  });

  const mutation = useMutation({
    mutationFn: async () => {
      const answer_key = keyInput.split(',').map((v) => v.trim().toUpperCase());
      await api.post('/exam-sets/', { exam: examId, set_code: setCode, answer_key });
    },
    onSuccess: () => {
      query.refetch();
    }
  });

  return (
    <Layout>
      <h1>Answer Keys</h1>
      <Form
        onSubmit={(e) => {
          e.preventDefault();
          mutation.mutate();
        }}
        className="d-flex gap-2 mb-3"
      >
        <Form.Control value={setCode} onChange={(e) => setSetCode(e.target.value)} placeholder="Set" maxLength={1} />
        <Form.Control
          value={keyInput}
          onChange={(e) => setKeyInput(e.target.value)}
          placeholder="Comma-separated answers"
        />
        <Button type="submit">Save</Button>
      </Form>
      <Table bordered>
        <thead>
          <tr>
            <th>Set</th>
            <th>Answer Key</th>
          </tr>
        </thead>
        <tbody>
          {query.data?.map((set) => (
            <tr key={set.id}>
              <td>{set.set_code}</td>
              <td>{set.answer_key.join(', ')}</td>
            </tr>
          ))}
        </tbody>
      </Table>
    </Layout>
  );
}
