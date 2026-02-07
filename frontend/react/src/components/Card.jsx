import React from "react";

const Card = ({ className = "", children, ...props }) => (
  <div className={`card ${className}`.trim()} {...props}>
    {children}
  </div>
);

export default Card;
