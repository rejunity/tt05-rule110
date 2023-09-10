`default_nettype none

module rule110 (
    input  wire [2:0] in,
    output reg out
);
    always @(*) begin
        case(in)
            3'b000:  out = 1'b0; // ...
            3'b100:  out = 1'b0; // X..
            3'b111:  out = 1'b0; // XXX
            default:    
                out = 1'b1;
        endcase
    end
endmodule

module tt_um_rejunity_rule110 #( parameter MAX_COUNT = 24'd10_000_000 ) (
    input  wire [7:0] ui_in,    // Dedicated inputs - connected to the input switches
    output wire [7:0] uo_out,   // Dedicated outputs - connected to the 7 segment display
    input  wire [7:0] uio_in,   // IOs: Bidirectional Input path
    output wire [7:0] uio_out,  // IOs: Bidirectional Output path
    output wire [7:0] uio_oe,   // IOs: Bidirectional Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // will go high when the design is enabled
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

    wire reset = ! rst_n;

    always @(posedge clk) begin
        // if reset, set counter to 0
        if (reset) begin
        end else begin
        end
    end

    wire out_;
    assign uo_out[0] = out_;
    rule110 rule110(.in(ui_in[2:0]), .out(out_));

endmodule
