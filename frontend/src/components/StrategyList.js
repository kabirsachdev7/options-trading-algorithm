import React from "react";
import { Table } from "react-bootstrap";

const StrategyList = ({ strategies }) => {
  return (
    <Table striped bordered hover>
      <thead>
        <tr>
          <th>#</th>
          <th>Strategy</th>
          <th>Confidence</th>
          <th>Execution Steps</th>
        </tr>
      </thead>
      <tbody>
        {strategies.map((strategy, index) => (
          <tr key={index}>
            <td>{index + 1}</td>
            <td>{strategy.name}</td>
            <td>{strategy.confidence}</td>
            <td>{strategy.execution}</td>
          </tr>
        ))}
      </tbody>
    </Table>
  );
};

export default StrategyList;
