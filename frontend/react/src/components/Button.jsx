import React from "react";

const Button = ({ className = "", children, ...props }) => (
  <button className={`btn ${className}`.trim()} {...props}>
    {children}
  </button>
);

export default Button;
