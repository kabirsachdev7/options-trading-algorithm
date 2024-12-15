import React, { useState } from "react";
import { DragDropContext, Droppable, Draggable } from "react-beautiful-dnd";

function StrategyBuilder() {
  const [legs, setLegs] = useState([]);

  const addLeg = (leg) => {
    setLegs([...legs, leg]);
  };

  const onDragEnd = (result) => {
    // Handle reordering of legs
  };

  return (
    <div>
      <h2>Strategy Builder</h2>
      <button
        onClick={() => addLeg({ type: "Call", action: "Buy", strike: 100 })}
      >
        Add Leg
      </button>
      <DragDropContext onDragEnd={onDragEnd}>
        <Droppable droppableId="legs">
          {(provided) => (
            <div {...provided.droppableProps} ref={provided.innerRef}>
              {legs.map((leg, index) => (
                <Draggable
                  key={index}
                  draggableId={`leg-${index}`}
                  index={index}
                >
                  {(provided) => (
                    <div
                      ref={provided.innerRef}
                      {...provided.draggableProps}
                      {...provided.dragHandleProps}
                    >
                      {leg.action} {leg.type} at Strike {leg.strike}
                    </div>
                  )}
                </Draggable>
              ))}
              {provided.placeholder}
            </div>
          )}
        </Droppable>
      </DragDropContext>
      {/* Implement visualization and risk assessment */}
    </div>
  );
}

export default StrategyBuilder;
