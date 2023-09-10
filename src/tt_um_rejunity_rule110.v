`define WRAP_AROUND_CELLS

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

module tt_um_rejunity_rule110 #( parameter NUM_CELLS = 32 ) (
    input  wire [7:0] ui_in,    // Dedicated inputs - connected to the input switches
    output wire [7:0] uo_out,   // Dedicated outputs - connected to the 7 segment display
    input  wire [7:0] uio_in,   // IOs: Bidirectional Input path
    output wire [7:0] uio_out,  // IOs: Bidirectional Output path
    output wire [7:0] uio_oe,   // IOs: Bidirectional Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // will go high when the design is enabled
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);
    // double buffer cells for now, TODO: try to get away with the single cells register in the future
    reg [NUM_CELLS+2-1:0] cells;  // cells state at time T
    reg [NUM_CELLS-1  :0] cells_; // cells state at time T-1

    assign uio_oe[7:0] = {8{1'b1}};
    wire reset = ! rst_n;

    // initialise cells
    // handle "recurrent connection" by passing state of the cell from T-1 to T
    always @(posedge clk) begin
        // if reset, initialise cells from the inputs
        if (reset) begin
            cells <= {{(NUM_CELLS+2-8-1){1'b0}}, ui_in[7:0], 1'b0};
        end else begin
            `ifdef WRAP_AROUND_CELLS
                cells <= {cells_[0], cells_, cells_[NUM_CELLS-1]}; // wrap-around cells
            `else
                cells <= {1'b0, cells_, 1'b0};
            `endif
        end
    end

    // apply rule110 to cells
    genvar i;
    generate
        for (i = 0; i < NUM_CELLS; i = i + 1) begin
            rule110 rule110(
                .in (cells[i+2:i]),
                .out(cells_[i])
                );
        end
    endgenerate

    // connect outputs to cells
    assign uo_out[7:0] = cells_[7:0];
    assign uio_out[7:0] = cells_[15:8];


    // USE this to test rule110 against truth-table
    // wire out_;
    // assign uo_out[0] = out_;
    // rule110 rule110(.in(ui_in[2:0]), .out(out_));

endmodule
