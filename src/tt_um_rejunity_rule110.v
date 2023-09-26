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

// For read & write cell data is arranged in blocks of 8 cells, addressed according to 'address_in' pins of the BIDIRECTIONAL path.
// Read results of the cellular automata from the OUTPUT path.
// Write results via INPUT path while holding 'write_enable_n' low
// Hold 'halt_n" low to pause execution of the cellular automata.
//
// Use INPUT pins to upload cell data
// [0..7] = 'data_in'        -- when 'write_enable_n' is pulled low the of 'data_in' contents are stored into the cells according to 'address_in', otherwise ignored
//
// Use OUTPUT pins to read out cell data
// [0..7] = 'data_out'       -- connected to the results of the cellular automata according to 'address_in'
//
// Use BIDIRECTIONAL pins for control and to specify block address
//  [0]   = 'write_enable_n' -- when pulled low `data_in` will be stored into the cells according to 'address_in'
//  [1]   = 'halt_n'         -- when pulled low time stops and cellular automata does not advance, useful when reading/writing multiple cell blocks
// [2..7] = 'address_in'     -- address of the cell block for reading or writing

module tt_um_rejunity_rule110 #( parameter NUM_CELLS = 64 ) (
    input  wire [7:0] ui_in,    // Dedicated INPUTs - connected to the input switches
    output wire [7:0] uo_out,   // Dedicated OUTPUTs - connected to the 7 segment display
    input  wire [7:0] uio_in,   // IOs: BIDIRECTIONAL Input path
    output wire [7:0] uio_out,  // IOs: BIDIRECTIONAL Output path
    output wire [7:0] uio_oe,   // IOs: BIDIRECTIONAL Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // will go high when the design is enabled
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);
    localparam MAX_ADDRESS_BITS = 6;
    localparam CELLS_PER_BLOCK = 8;
    localparam CELL_BLOCK_ADDRESS_BITS = $clog2(NUM_CELLS / CELLS_PER_BLOCK);
    // unfortunately only in SystemVerilog: assert (CELL_BLOCK_ADDRESS_BITS <= MAX_ADDRESS_BITS); 

    // double buffer cells, at time T and T+1
    // support horizontal wrap-around by adding two additional cells, one on each side of the buffer
    // hope that compiler will be smart enough and instantiate flip-flops only for one of the buffers
    reg [NUM_CELLS+2-1:0] cells;    // cells state at time T
    reg [NUM_CELLS-1  :0] cells_dt; // cells state at time T+1
    localparam RESET_STATE = {{(NUM_CELLS){1'b0}}, 1'b1, 1'b0}; // on reset set all cells _except one_ to 0

    wire reset = ! rst_n;

    assign uio_oe[7:0] = {8{1'b0}}; // BIDIRECTIONAL path set to input
    assign uio_out[7:0] = {8{1'b0}}; // Initialise unused outputs of the BIDIRECTIONAL path to 0 for posterity (otherwise Yosys fails)
    wire write_enable = ! uio_in[0];
    wire halt = ! uio_in[1];
    wire [7:0] data_in = ui_in[7:0];
    wire [CELL_BLOCK_ADDRESS_BITS-1:0] address_in_ = uio_in[CELL_BLOCK_ADDRESS_BITS-1+2:2];
    wire [CELL_BLOCK_ADDRESS_BITS-1:0] address_in = (&address_in_ == 1) ? 0: address_in_;  // if address pins are not driven, set address to 0

    always @(posedge clk) begin
        if (reset) begin
            cells <= RESET_STATE;
        end else if (write_enable) begin
            cells[address_in*CELLS_PER_BLOCK + 1 +: CELLS_PER_BLOCK] <= data_in;
        end else if (!halt) begin
            // advance cellular automata by copying results from the previous iteration into the time T buffer
            `ifdef WRAP_AROUND_CELLS
                cells <= {cells_dt[0], cells_dt, cells_dt[NUM_CELLS-1]}; // wrap-around cells
            `else
                cells <= {1'b0, cells_dt, 1'b0};                         // otherwise pad with 0
            `endif
        end
    end

    // apply rule110 to cells
    genvar i;
    generate
        for (i = 0; i < NUM_CELLS; i = i + 1) begin
            rule110 rule110(
                .in (cells[i+2:i]),
                .out(cells_dt[i])
                );
        end
    endgenerate

    // connect chip output pins to T+1 cells according to the specified block address
    //assign uo_out[7:0] = cells_dt[address_in*CELLS_PER_BLOCK +: CELLS_PER_BLOCK];
    assign uo_out[7:0] = cells[address_in*CELLS_PER_BLOCK +: CELLS_PER_BLOCK];

    // USE this to test rule110 against truth-table
    // wire out_;
    // assign uo_out[0] = out_;
    // rule110 rule110(.in(ui_in[2:0]), .out(out_));

endmodule
